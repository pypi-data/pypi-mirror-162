from typing import Text
from packaging import version
from dataclasses import dataclass

from bf_nlu_banki.shared.exceptions import bf_nlu_bankiException
from bf_nlu_banki.constants import MINIMUM_COMPATIBLE_VERSION


@dataclass
class UnsupportedModelVersionError(bf_nlu_bankiException):
    """Raised when a model is too old to be loaded.

    Args:
        model_version: the used model version that is not supported and triggered
            this exception
    """

    model_version: Text

    def __str__(self) -> Text:
        minimum_version = version.parse(MINIMUM_COMPATIBLE_VERSION)
        return (
            f"The model version is trained using bf_nlu_banki Open Source {self.model_version} "
            f"and is not compatible with your current installation "
            f"which supports models build with bf_nlu_banki Open Source {minimum_version} "
            f"or higher. "
            f"This means that you either need to retrain your model "
            f"or revert back to the bf_nlu_banki version that trained the model "
            f"to ensure that the versions match up again."
        )


class ModelNotFound(bf_nlu_bankiException):
    """Raised when a model is not found in the path provided by the user."""


class NoEventsToMigrateError(bf_nlu_bankiException):
    """Raised when no events to be migrated are found."""


class NoConversationsInTrackerStoreError(bf_nlu_bankiException):
    """Raised when a tracker store does not contain any conversations."""


class NoEventsInTimeRangeError(bf_nlu_bankiException):
    """Raised when a tracker store does not contain events within a given time range."""


class MissingDependencyException(bf_nlu_bankiException):
    """Raised if a python package dependency is needed, but not installed."""


@dataclass
class PublishingError(bf_nlu_bankiException):
    """Raised when publishing of an event fails.

    Attributes:
        timestamp -- Unix timestamp of the event during which publishing fails.
    """

    timestamp: float

    def __str__(self) -> Text:
        """Returns string representation of exception."""
        return str(self.timestamp)


class ActionLimitReached(bf_nlu_bankiException):
    """Raised when predicted action limit is reached."""
