from django.test import TestCase
from Fuseki.fuseki import Fuseki
from vocabularies.models import Vocabulary
from Migration.migration_context import MigrationContext
from Migration.backup_migration_strategy import BackupMigrationStrategy


class FusekiTestCase(TestCase):

    def setUp(self) -> None:
        self.fuseki_dev = Fuseki(
            'fuseki-dev', 3030, 'development', 'fuseki-dev/backup')
        self.vocabulary = Vocabulary(name='ds')
        self.vocabulary.save()
        # self.fuseki_dev.create_vocabulary(self.vocabulary)

    def test_get_copy_tasks(self):
        context = MigrationContext(BackupMigrationStrategy())
        context.start(self.vocabulary)
        self.assertTrue(True)
