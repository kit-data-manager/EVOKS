from datetime import datetime
from unittest.case import skip
from django.test import TestCase
from Fuseki.fuseki import Fuseki
from Fuseki.task import Task
from Fuseki.copy import Copy

from vocabularies.models import Vocabulary
from time import sleep
import os
from unittest.mock import patch
import io
import random
import string


class FusekiTestCase(TestCase):

    def setUp(self) -> None:
        self.fuseki_dev = Fuseki(
            'fuseki-dev', 3030, 'development', 'fuseki-dev/backup')
        self.vocabulary = Vocabulary(name=''.join(random.choices(string.ascii_letters, k=10)))
        self.vocabulary.save()
        self.fuseki_dev.create_vocabulary(self.vocabulary)
        self.delete_vocabularies = [self.vocabulary]

    def tearDown(self) -> None:
        # remove all backup files
        for f in os.listdir(self.fuseki_dev.backup_path):
            os.remove(os.path.join(self.fuseki_dev.backup_path, f))
        # delete all datasets
        try:
            for vocab in self.delete_vocabularies:
                self.fuseki_dev.delete_vocabulary(vocab)
        except:  # will fail when running the test_delete_vocabulary testcase
            pass

    def test_constructor(self):

        # all attributes set correctly
        self.assertEqual(self.fuseki_dev.host, 'fuseki-dev')
        self.assertEqual(self.fuseki_dev.port, 3030)
        self.assertEqual(self.fuseki_dev.environment, 'development')

        # api_url and url 'calculated'
        self.assertIsNotNone(self.fuseki_dev.api_url)
        self.assertIsNotNone(self.fuseki_dev.url)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_constructor_bad_host(self, mock_stdout):

        Fuseki('fuseki-wont-work', 3030, 'development', 'fuseki-dev/backup')

        self.assertEqual(mock_stdout.getvalue(),
                         'Invalid Fuseki configuration. Failed to ping server\n')

    def test_sparql_endpoint(self):
        url = self.fuseki_dev.build_sparql_endpoint(self.vocabulary)
        self.assertIsNotNone(url)

    def test_sparql_endpoint_live(self):
        url = self.fuseki_dev.build_sparql_endpoint(self.vocabulary, True)
        self.assertIsNotNone(url)

    def test_get_copy_tasks(self):
        task_id = self.fuseki_dev.start_vocabulary_copy(self.vocabulary)
        self.assertIsNotNone(task_id)

    def test_get_copy(self):

        task_id = self.fuseki_dev.start_vocabulary_copy(self.vocabulary)
        tasks = self.fuseki_dev.get_copy_tasks()

        task = None
        while task is not None:
            task = next((task for task in tasks if task.id is task_id), None)
            sleep(0.25)

        copy = self.fuseki_dev.get_copy(task, self.vocabulary)
        self.assertTrue(os.path.exists(copy.path))

    def test_get_non_existing_copy(self):
        v = Vocabulary(name='cool_vocabulary999')
        v.save()
        self.delete_vocabularies.append(v)
        task = Task('backup', '-1', datetime.now(), datetime.now(), True)
        self.assertRaises(
            ValueError, self.fuseki_dev.get_copy, task, v)

    def test_delete_vocabulary(self):
        self.fuseki_dev.delete_vocabulary(self.vocabulary)
        try:
            self.fuseki_dev.create_vocabulary(self.vocabulary)
            self.fuseki_dev.delete_vocabulary(self.vocabulary)
        except:
            self.fail('Vocabulary did not get deleted')

    def test_delete_bad_vocabulary(self):
        v = Vocabulary(name='cool_vocabulary26')
        v.save()
        self.fuseki_dev.delete_vocabulary(self.vocabulary)
        # deleting the second time should fail
        self.assertRaises(
            ValueError, self.fuseki_dev.delete_vocabulary, self.vocabulary)

    def test_create_duplicate_vocabulary(self):
        v = Vocabulary(name='cool_vocabulary26')
        v.save()
        self.delete_vocabularies.append(v)

        self.fuseki_dev.create_vocabulary(v)
        self.assertRaises(ValueError, self.fuseki_dev.create_vocabulary, v)

    def test_create_vocabulary(self):
        v = Vocabulary(name='cool_vocabulary')
        v.save()
        self.delete_vocabularies.append(v)
        try:
            self.fuseki_dev.create_vocabulary(v)
        except Exception as e:
            self.fail('Creating vocabulary failed ' + str(e))

    def test_restore_copy(self):

        try:
            source = Vocabulary(name='ds_source')
            source.save()
            self.delete_vocabularies.append(source)

            target = Vocabulary(name='ds_target')
            target.save()
            self.delete_vocabularies.append(target)

            self.fuseki_dev.create_vocabulary(source)

            task_id = self.fuseki_dev.start_vocabulary_copy(source)

            tasks = self.fuseki_dev.get_copy_tasks()
            task = next((task for task in tasks if task.id ==
                        task_id and task.success == True), None)
            while task is None:
                task = next(
                    (task for task in tasks if task.id == task_id), None)
                tasks = self.fuseki_dev.get_copy_tasks()
                sleep(0.25)

            copy = self.fuseki_dev.get_copy(task, source)

            self.fuseki_dev.restore_copy(target, copy)
            self.fuseki_dev.delete_vocabulary(target, True)
            self.fuseki_dev.delete_vocabulary(source)
            copy.delete()
        except Exception as e:
            self.fail('Restoring vocabulary failed '+str(e))

    def test_start_bad_vocabulary_copy(self):
        source = Vocabulary(name='ds_source23')
        source.save()
        self.delete_vocabularies.append(source)
        self.assertRaises(
            Exception, self.fuseki_dev.start_vocabulary_copy, source)

    def test_query(self):
        try:
            results = self.fuseki_dev.query(
                self.vocabulary,
                """
                prefix owl: <http://www.w3.org/2002/07/owl#>
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT DISTINCT ?class ?label ?description
                WHERE {
                ?class a owl:Class.
                OPTIONAL { ?class rdfs:label ?label}
                OPTIONAL { ?class rdfs:comment ?description}
                }
                LIMIT 25
            """, 'json')
            self.assertIsNotNone(results)

        except Exception as e:
            self.fail('Query failed: ' + str(e))

    def test_delete_bad_copy(self):
        task = Task('backup', '-1', datetime.now(), datetime.now(), True)

        copy = Copy(task, 'thispathdoesnotexist.txt')
        self.assertRaises(ValueError, copy.delete)
