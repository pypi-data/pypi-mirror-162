import logging
from typing import Text

from bf_nlu_banki.shared.exceptions import bf_nlu_bankiException


logger = logging.getLogger(__name__)


# TODO: remove/move
class InvalidModelError(bf_nlu_bankiException):
    """Raised when a model failed to load.

    Attributes:
        message -- explanation of why the model is invalid
    """

    def __init__(self, message: Text) -> None:
        """Initialize message attribute."""
        self.message = message
        super(InvalidModelError, self).__init__(message)

    def __str__(self) -> Text:
        return self.message
