from bf_nlu_banki.nlu.classifiers.diet_classifier import DIETClassifier
from bf_nlu_banki.nlu.classifiers.fallback_classifier import FallbackClassifier
from bf_nlu_banki.nlu.classifiers.keyword_intent_classifier import KeywordIntentClassifier
from bf_nlu_banki.nlu.classifiers.logistic_regression_classifier import (
    LogisticRegressionClassifier,
)
from bf_nlu_banki.nlu.classifiers.mitie_intent_classifier import MitieIntentClassifier
from bf_nlu_banki.nlu.classifiers.sklearn_intent_classifier import SklearnIntentClassifier
from bf_nlu_banki.nlu.extractors.crf_entity_extractor import CRFEntityExtractor
from bf_nlu_banki.nlu.extractors.duckling_entity_extractor import DucklingEntityExtractor
from bf_nlu_banki.nlu.extractors.entity_synonyms import EntitySynonymMapper
from bf_nlu_banki.nlu.extractors.mitie_entity_extractor import MitieEntityExtractor
from bf_nlu_banki.nlu.extractors.spacy_entity_extractor import SpacyEntityExtractor
from bf_nlu_banki.nlu.extractors.regex_entity_extractor import RegexEntityExtractor
from bf_nlu_banki.nlu.featurizers.sparse_featurizer.lexical_syntactic_featurizer import (
    LexicalSyntacticFeaturizer,
)
from bf_nlu_banki.nlu.featurizers.dense_featurizer.convert_featurizer import ConveRTFeaturizer
from bf_nlu_banki.nlu.featurizers.dense_featurizer.mitie_featurizer import MitieFeaturizer
from bf_nlu_banki.nlu.featurizers.dense_featurizer.spacy_featurizer import SpacyFeaturizer
from bf_nlu_banki.nlu.featurizers.sparse_featurizer.count_vectors_featurizer import (
    CountVectorsFeaturizer,
)
from bf_nlu_banki.nlu.featurizers.dense_featurizer.lm_featurizer import LanguageModelFeaturizer
from bf_nlu_banki.nlu.featurizers.sparse_featurizer.regex_featurizer import RegexFeaturizer
from bf_nlu_banki.nlu.selectors.response_selector import ResponseSelector
from bf_nlu_banki.nlu.tokenizers.jieba_tokenizer import JiebaTokenizer
from bf_nlu_banki.nlu.tokenizers.mitie_tokenizer import MitieTokenizer
from bf_nlu_banki.nlu.tokenizers.spacy_tokenizer import SpacyTokenizer
from bf_nlu_banki.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from bf_nlu_banki.nlu.utils.mitie_utils import MitieNLP
from bf_nlu_banki.nlu.utils.spacy_utils import SpacyNLP


from bf_nlu_banki.core.policies.ted_policy import TEDPolicy
from bf_nlu_banki.core.policies.memoization import MemoizationPolicy, AugmentedMemoizationPolicy
from bf_nlu_banki.core.policies.rule_policy import RulePolicy
from bf_nlu_banki.core.policies.unexpected_intent_policy import UnexpecTEDIntentPolicy

DEFAULT_COMPONENTS = [
    # Message Classifiers
    DIETClassifier,
    FallbackClassifier,
    KeywordIntentClassifier,
    MitieIntentClassifier,
    SklearnIntentClassifier,
    LogisticRegressionClassifier,
    # Response Selectors
    ResponseSelector,
    # Message Entity Extractors
    CRFEntityExtractor,
    DucklingEntityExtractor,
    EntitySynonymMapper,
    MitieEntityExtractor,
    SpacyEntityExtractor,
    RegexEntityExtractor,
    # Message Feauturizers
    LexicalSyntacticFeaturizer,
    ConveRTFeaturizer,
    MitieFeaturizer,
    SpacyFeaturizer,
    CountVectorsFeaturizer,
    LanguageModelFeaturizer,
    RegexFeaturizer,
    # Tokenizers
    JiebaTokenizer,
    MitieTokenizer,
    SpacyTokenizer,
    WhitespaceTokenizer,
    # Language Model Providers
    MitieNLP,
    SpacyNLP,
    # Dialogue Management Policies
    TEDPolicy,
    UnexpecTEDIntentPolicy,
    RulePolicy,
    MemoizationPolicy,
    AugmentedMemoizationPolicy,
]
