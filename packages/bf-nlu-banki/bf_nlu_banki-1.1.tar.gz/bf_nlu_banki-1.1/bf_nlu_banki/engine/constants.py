from typing import List

from bf_nlu_banki.core.channels import UserMessage
from bf_nlu_banki.shared.core.trackers import DialogueStateTracker
from bf_nlu_banki.shared.importers.importer import TrainingDataImporter

PLACEHOLDER_IMPORTER = "__importer__"
PLACEHOLDER_MESSAGE = "__message__"
PLACEHOLDER_TRACKER = "__tracker__"
RESERVED_PLACEHOLDERS = {
    PLACEHOLDER_IMPORTER: TrainingDataImporter,
    PLACEHOLDER_MESSAGE: List[UserMessage],
    PLACEHOLDER_TRACKER: DialogueStateTracker,
}
