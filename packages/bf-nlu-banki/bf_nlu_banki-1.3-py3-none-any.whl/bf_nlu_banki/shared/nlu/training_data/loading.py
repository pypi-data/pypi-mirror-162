import json
import logging
import os
import typing
from typing import Optional, Text, Callable, Dict, Any, List

import bf_nlu_banki.shared.utils.io as bff
from bf_nlu_banki.shared.nlu.training_data.formats.dialogflow import (
    DIALOGFLOW_AGENT,
    DIALOGFLOW_ENTITIES,
    DIALOGFLOW_ENTITY_ENTRIES,
    DIALOGFLOW_INTENT,
    DIALOGFLOW_INTENT_EXAMPLES,
    DIALOGFLOW_PACKAGE,
)
from bf_nlu_banki.shared.nlu.training_data.training_data import TrainingData

if typing.TYPE_CHECKING:
    from bf_nlu_banki.shared.nlu.training_data.formats.readerwriter import TrainingDataReader

logger = logging.getLogger(__name__)

# Different supported file formats and their identifier
WIT = "wit"
LUIS = "luis"
bf_nlu_banki = "bf_nlu_banki_nlu"
bf_nlu_banki_YAML = "bf_nlu_banki_yml"
UNK = "unk"
DIALOGFLOW_RELEVANT = {DIALOGFLOW_ENTITIES, DIALOGFLOW_INTENT}

_json_format_heuristics: Dict[Text, Callable[[Any, Text], bool]] = {
    WIT: lambda js, fn: "utterances" in js and "luis_schema_version" not in js,
    LUIS: lambda js, fn: "luis_schema_version" in js,
    bf_nlu_banki: lambda js, fn: "bf_nlu_banki_nlu_data" in js,
    DIALOGFLOW_AGENT: lambda js, fn: "supportedLanguages" in js,
    DIALOGFLOW_PACKAGE: lambda js, fn: "version" in js and len(js) == 1,
    DIALOGFLOW_INTENT: lambda js, fn: "responses" in js,
    DIALOGFLOW_ENTITIES: lambda js, fn: "isEnum" in js,
    DIALOGFLOW_INTENT_EXAMPLES: lambda js, fn: "_usersays_" in fn,
    DIALOGFLOW_ENTITY_ENTRIES: lambda js, fn: "_entries_" in fn,
}


def load_data(resource_name: Text, language: Optional[Text] = "en") -> "TrainingData":
    """Load training data from disk.

    Merges them if loaded from disk and multiple files are found."""
    if not os.path.exists(resource_name):
        raise ValueError(f"File '{resource_name}' does not exist.")

    if os.path.isfile(resource_name):
        files = [resource_name]
    else:
        files = bf_nlu_banki.shared.utils.io.list_files(resource_name)

    data_sets = [_load(f, language) for f in files]
    training_data_sets: List[TrainingData] = [ds for ds in data_sets if ds]
    if len(training_data_sets) == 0:
        training_data = TrainingData()
    elif len(training_data_sets) == 1:
        training_data = training_data_sets[0]
    else:
        training_data = training_data_sets[0].merge(*training_data_sets[1:])

    return training_data


def _reader_factory(fformat: Text) -> Optional["TrainingDataReader"]:
    """Generates the appropriate reader class based on the file format."""
    from bf_nlu_banki.shared.nlu.training_data.formats.bf_nlu_banki_yaml import (
        bf_nlu_bankiYAMLReader,
        
    )
    from bf_nlu_banki.shared.nlu.training_data.formats.wit import (
        WitReader,
        
    )
    from bf_nlu_banki.shared.nlu.training_data.formats.dialogflow import (
        
        DialogflowReader,
    )
    from bf_nlu_banki.shared.nlu.training_data.formats.luis import (
        LuisReader,
    )
    from bf_nlu_banki.shared.nlu.training_data.formats.bf_nlu_banki import (
        bf_nlu_bankiReader,
        
    )

    reader: Optional["TrainingDataReader"] = None
    if fformat == LUIS:
        reader = LuisReader()
    elif fformat == WIT:
        reader = WitReader()
    elif fformat in DIALOGFLOW_RELEVANT:
        reader = DialogflowReader()
    elif fformat == bf_nlu_banki:
        reader = bf_nlu_bankiReader()
    elif fformat == bf_nlu_banki_YAML:
        reader = bf_nlu_bankiYAMLReader()
    return reader


def _load(filename: Text, language: Optional[Text] = "en") -> Optional["TrainingData"]:
    """Loads a single training data file from disk."""

    fformat = guess_format(filename)
    if fformat == UNK:
        raise ValueError(f"Unknown data format for file '{filename}'.")

    reader = _reader_factory(fformat)

    if reader:
        return reader.read(filename, language=language, fformat=fformat)
    else:
        return None


def guess_format(filename: Text) -> Text:
    """Applies heuristics to guess the data format of a file.

    Args:
        filename: file whose type should be guessed

    Returns:
        Guessed file format.
    """
    from bf_nlu_banki.shared.nlu.training_data.formats.bf_nlu_banki_yaml import bf_nlu_bankiYAMLReader

    guess = UNK

    if not os.path.isfile(filename):
        return guess

    try:
        content = bff.read_file(filename)
        js = json.loads(content)
    except ValueError:
        if bf_nlu_bankiYAMLReader.is_yaml_nlu_file(filename):
            guess = bf_nlu_banki_YAML
    else:
        for file_format, format_heuristic in _json_format_heuristics.items():
            if format_heuristic(js, filename):
                guess = file_format
                break

    logger.debug(f"Training data format of '{filename}' is '{guess}'.")

    return guess
