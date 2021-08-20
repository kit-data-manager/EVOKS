from Skosmos.skosmos_vocabulary_config import SkosmosVocabularyConfig
from vocabularies.models import Vocabulary
from .migration_strategy import MigrationStrategy
from evoks.fuseki import fuseki_dev, fuseki_live
from time import sleep
from evoks.skosmos import skosmos_live


class BackupMigrationStrategy(MigrationStrategy):
    def start(self, vocabulary: Vocabulary):

        task_id = fuseki_dev.start_vocabulary_copy(vocabulary)

        tasks = fuseki_dev.get_copy_tasks()
        task = None
        while task is None:
            tasks = fuseki_dev.get_copy_tasks()
            task = next((task for task in tasks if task.id == task_id), None)
            sleep(0.25)

        copy = fuseki_dev.get_copy(task, vocabulary)

        fuseki_live.restore_copy(vocabulary, copy)
        top_lang = vocabulary.get_top_language()
        languages = vocabulary.get_languages()
        config = SkosmosVocabularyConfig('cat_general', vocabulary.name_with_version(), vocabulary.name_with_version(), languages,
                                         fuseki_live.build_sparql_endpoint(vocabulary, True), vocabulary.urispace, top_lang)

        skosmos_live.add_vocabulary(config)

        copy.delete()
