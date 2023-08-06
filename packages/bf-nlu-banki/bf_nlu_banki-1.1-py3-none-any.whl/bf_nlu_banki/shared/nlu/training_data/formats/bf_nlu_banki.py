import logging
from collections import defaultdict
from typing import Any, Dict, Text

from bf_nlu_banki.shared.constants import DOCS_URL_MIGRATION_GUIDE
from bf_nlu_banki.shared.nlu.constants import TEXT, INTENT, ENTITIES
from bf_nlu_banki.shared.nlu.training_data.formats.readerwriter import (
    JsonTrainingDataReader,
    TrainingDataWriter,
)
from bf_nlu_banki.shared.nlu.training_data.util import transform_entity_synonyms
from bf_nlu_banki.shared.utils.io import json_to_string

from bf_nlu_banki.shared.nlu.training_data.training_data import TrainingData
from bf_nlu_banki.shared.nlu.training_data.message import Message
import bf_nlu_banki.shared.utils.io

logger = logging.getLogger(__name__)


class bf_nlu_bankiReader(JsonTrainingDataReader):
    """Reader for bf_nlu_banki NLU training data in JSON format.

    Example:
        {
          "bf_nlu_banki_nlu_data": {
            "regex_features": [
              {
                "name": "zipcode",
                "pattern": "[0-9]{5}"
              }
            ],
            "entity_synonyms": [
              {
                "value": "chinese",
                "synonyms": ["Chinese", "Chines", "chines"]
              }
            ],
            "common_examples": [
              {
                "text": "hey",
                "intent": "greet",
                "entities": []
              },
              {
                "text": "howdy",
                "intent": "greet",
                "entities": []
              }
            ]
          }
        }
    """

    def __init__(self) -> None:
        """Creates reader."""
        super().__init__()
        bf_nlu_banki.shared.utils.io.raise_deprecation_warning(
            "NLU data in bf_nlu_banki JSON format is deprecated and will be removed in bf_nlu_banki "
            "Open Source 4.0.0. Please convert your JSON NLU data to the "
            "bf_nlu_banki YAML format.",
            docs=DOCS_URL_MIGRATION_GUIDE,
        )

    def read_from_json(self, js: Dict[Text, Any], **_: Any) -> "TrainingData":
        """Loads training data stored in the bf_nlu_banki NLU data format."""
        import bf_nlu_banki.shared.nlu.training_data.schemas.data_schema as schema
        import bf_nlu_banki.shared.utils.validation as validation_utils

        validation_utils.validate_training_data(js, schema.bf_nlu_banki_nlu_data_schema())

        data = js["bf_nlu_banki_nlu_data"]
        common_examples = data.get("common_examples", [])
        entity_synonyms = data.get("entity_synonyms", [])
        regex_features = data.get("regex_features", [])
        lookup_tables = data.get("lookup_tables", [])

        entity_synonyms = transform_entity_synonyms(entity_synonyms)

        training_examples = []
        for ex in common_examples:
            # taking care of custom entries
            msg = Message.build(
                text=ex.pop(TEXT, ""),
                intent=ex.pop(INTENT, None),
                entities=ex.pop(ENTITIES, None),
                **ex,
            )
            training_examples.append(msg)

        return TrainingData(
            training_examples, entity_synonyms, regex_features, lookup_tables
        )


class bf_nlu_bankiWriter(TrainingDataWriter):
    """Dumps NLU data as bf_nlu_banki JSON string."""

    def __init__(self) -> None:
        """Creates writer."""
        super().__init__()
        bf_nlu_banki.shared.utils.io.raise_deprecation_warning(
            "NLU data in bf_nlu_banki JSON format is deprecated and will be removed in bf_nlu_banki "
            "Open Source 4.0.0. Please convert your JSON NLU data to the "
            "bf_nlu_banki YAML format.",
            docs=DOCS_URL_MIGRATION_GUIDE,
        )

    def dumps(self, training_data: "TrainingData", **kwargs: Any) -> Text:
        """Writes Training Data to a string in json format."""
        js_entity_synonyms = defaultdict(list)
        for k, v in training_data.entity_synonyms.items():
            if k != v:
                js_entity_synonyms[v].append(k)

        formatted_synonyms = [
            {"value": value, "synonyms": syns}
            for value, syns in js_entity_synonyms.items()
        ]

        formatted_examples = [
            example.as_dict_nlu() for example in training_data.training_examples
        ]

        return json_to_string(
            {
                "bf_nlu_banki_nlu_data": {
                    "common_examples": formatted_examples,
                    "regex_features": training_data.regex_features,
                    "lookup_tables": training_data.lookup_tables,
                    "entity_synonyms": formatted_synonyms,
                }
            },
            **kwargs,
        )
