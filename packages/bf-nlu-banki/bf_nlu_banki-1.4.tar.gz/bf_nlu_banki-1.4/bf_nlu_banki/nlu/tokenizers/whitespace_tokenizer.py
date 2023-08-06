from __future__ import annotations
from typing import Any, Dict, List, Optional, Text

import regex

import bf_nlu_banki.shared.utils.io
import bf_nlu_banki.utils.io

from bf_nlu_banki.engine.graph import ExecutionContext
from bf_nlu_banki.engine.recipes.default_recipe import DefaultV1Recipe
from bf_nlu_banki.engine.storage.resource import Resource
from bf_nlu_banki.engine.storage.storage import ModelStorage
from bf_nlu_banki.nlu.tokenizers.tokenizer import Token, Tokenizer
from bf_nlu_banki.shared.constants import DOCS_URL_COMPONENTS
from bf_nlu_banki.shared.nlu.training_data.message import Message


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False
)
class WhitespaceTokenizer(Tokenizer):
    """Creates features for entity extraction."""

    @staticmethod
    def not_supported_languages() -> Optional[List[Text]]:
        """The languages that are not supported."""
        return ["zh", "ja", "th"]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns the component's default config."""
        return {
            # Flag to check whether to split intents
            "intent_tokenization_flag": False,
            # Symbol on which intent should be split
            "intent_split_symbol": "_",
            # Regular expression to detect tokens
            "token_pattern": None,
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initialize the tokenizer."""
        super().__init__(config)
        self.emoji_pattern = bf_nlu_banki.utils.io.get_emoji_regex()

        if "case_sensitive" in self._config:
            bf_nlu_banki.shared.utils.io.raise_warning(
                "The option 'case_sensitive' was moved from the tokenizers to the "
                "featurizers.",
                docs=DOCS_URL_COMPONENTS,
            )

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> WhitespaceTokenizer:
        """Creates a new component (see parent class for full docstring)."""
        # Path to the dictionaries on the local filesystem.
        return cls(config)

    def remove_emoji(self, text: Text) -> Text:
        """Remove emoji if the full text, aka token, matches the emoji regex."""
        match = self.emoji_pattern.fullmatch(text)

        if match is not None:
            return ""

        return text

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        # we need to use regex instead of re, because of
        # https://stackoverflow.com/questions/12746458/python-unicode-regular-expression-matching-failing-with-some-unicode-characters

        # remove 'not a word character' if
        words = regex.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()

        words = [self.remove_emoji(w) for w in words]
        words = [w for w in words if w]

        # if we removed everything like smiles `:)`, use the whole text as 1 token
        if not words:
            words = [text]

        tokens = self._convert_words_to_tokens(words, text)

        return self._apply_token_pattern(tokens)
