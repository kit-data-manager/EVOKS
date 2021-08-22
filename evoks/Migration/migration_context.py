from vocabularies.models import Vocabulary
from .migration_strategy import MigrationStrategy


class MigrationContext(MigrationStrategy):
    """
    Class that is responsible for the migration of a vocabulary and using the correct strategy 
    """

    def __init__(self, strategy: MigrationStrategy) -> None:
        """Creates a new MigrationContext with the given strategy

        Args:
            strategy (MigrationStrategy): the migration strategy to uses
        """
        self.strategy = strategy

    def start(self, vocabulary: Vocabulary):
        """Start the internal migration strategy

        Args:
            vocabulary (Vocabulary): the vocabulary to migrate
        """
        self.strategy.start(vocabulary)

    def set_migration_strategy(self, strategy: MigrationStrategy):
        """Set the migration strategy

        Args:
            strategy (MigrationStrategy): subclass of MigrationStrategy
        """
        self.strategy = strategy
