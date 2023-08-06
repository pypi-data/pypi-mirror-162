import logging

from bf_nlu_banki import version  # noqa: F401
from bf_nlu_banki.api import run, train, test  # noqa: F401

# define the version before the other imports since these need it
__version__ = version.__version__


logging.getLogger(__name__).addHandler(logging.NullHandler())
