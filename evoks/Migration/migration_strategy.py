from vocabularies.models import Vocabulary
from abc import ABC, abstractmethod


class MigrationStrategy(ABC):
    """MigrationStrategy is an abstract class that defines the interface all strategies need to implement
    """

    @abstractmethod
    def start(self, vocabulary: Vocabulary):
        """Abstract method that is called when a strategy is started

        Args:
            vocabulary (Vocabulary): Vocabulary to migrate
        """
