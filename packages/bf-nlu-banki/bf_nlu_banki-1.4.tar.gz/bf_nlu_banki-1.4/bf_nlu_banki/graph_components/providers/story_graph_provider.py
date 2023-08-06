from __future__ import annotations
from typing import Dict, Text, Any

from bf_nlu_banki.engine.graph import GraphComponent, ExecutionContext
from bf_nlu_banki.engine.storage.resource import Resource
from bf_nlu_banki.engine.storage.storage import ModelStorage
from bf_nlu_banki.shared.core.training_data.structures import StoryGraph
from bf_nlu_banki.shared.importers.importer import TrainingDataImporter


class StoryGraphProvider(GraphComponent):
    """Provides the training data from stories."""

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Creates provider from config."""
        self._config = config

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns default configuration (see parent class for full docstring)."""
        return {"exclusion_percentage": None}

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> StoryGraphProvider:
        """Creates component (see parent class for full docstring)."""
        return cls(config)

    def provide(self, importer: TrainingDataImporter) -> StoryGraph:
        """Provides the story graph from the training data.

        Args:
            importer: instance of TrainingDataImporter.

        Returns:
            The story graph containing stories and rules used for training.
        """
        return importer.get_stories(**self._config)
