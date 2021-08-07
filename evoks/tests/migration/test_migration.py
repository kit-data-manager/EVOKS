from django.test import TestCase
from Fuseki.fuseki import Fuseki
from vocabularies.models import Vocabulary
from Migration.migration_context import MigrationContext
from Migration.backup_migration_strategy import BackupMigrationStrategy
from time import sleep
import unittest
import os
from evoks.skosmos import skosmos_live


class FusekiTestCase(TestCase):

    def setUp(self) -> None:
        self.fuseki_dev = Fuseki(
            'fuseki-dev', 3030, 'development', 'fuseki-dev/backup')
        self.fuseki_live = Fuseki(
            'fuseki-live', 3030, 'production', 'fuseki-dev/backup')

        self.vocabulary = Vocabulary(name='vokabular34')
        self.vocabulary.save()
        self.fuseki_dev.create_vocabulary(self.vocabulary)
        sleep(5)
        self.delete_vocabularies = [self.vocabulary]

    def tearDown(self) -> None:
        # remove all backup files
        for f in os.listdir(self.fuseki_dev.backup_path):
            os.remove(os.path.join(self.fuseki_dev.backup_path, f))
        # delete all datasets
        try:
            for vocab in self.delete_vocabularies:
                self.fuseki_dev.delete_vocabulary(vocab)
        except:
            pass
        skosmos_live.delete_vocabulary(self.vocabulary.name)

    def test_migration(self):
        context = MigrationContext(BackupMigrationStrategy())
        context.start(self.vocabulary)
        self.assertTrue(True)
        self.fuseki_live.delete_vocabulary(self.vocabulary)

    def test_set_strategy(self):
        context = MigrationContext(None)
        context.set_migration_strategy(BackupMigrationStrategy())
        self.assertIsNotNone(context.strategy)
