from abc import ABC
import scipy.sparse
from bf_nlu_banki.nlu.featurizers.featurizer import Featurizer


class SparseFeaturizer(Featurizer[scipy.sparse.spmatrix], ABC):
    """Base class for all sparse featurizers."""

    pass
