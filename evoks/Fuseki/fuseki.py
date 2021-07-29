from typing import List, Optional

from requests import auth
from vocabularies.models import Vocabulary
from SPARQLWrapper import SPARQLWrapper, XML, JSON
import requests
from .task import Task
from .copy import Copy
from http import HTTPStatus
import os
from django.conf import settings

user = settings.FUSEKI_USER
password = settings.FUSEKI_PASSWORD


class Fuseki:

    def __init__(self, host: str, port: int, environment: str, backup_path: str) -> None:
        """
        Creates a new Fuseki object

        Args:
            host (str): Host of Fuseki server
            port (int): Port of Fuseki server
            environment (str): Environment of server
            backup_path (str): Relative path to the backup folder

        Raises:
            ValueError: Fuseki server is not reachable under the given Host+Port
        """
        self.host = host
        self.port = port
        self.environment = environment
        self.url = 'http://{host}:{port}/'.format(host=host, port=port)
        self.api_url = '{url}$/'.format(url=self.url)
        self.backup_path = os.path.join(settings.DOCKER_BASE_DIR, backup_path)

        valid = self.ping()
        if not valid:
            raise ValueError(
                'Invalid Fuseki configuration. Failed to ping server')

    def build_sparql_endpoint(self, vocabulary: Vocabulary) -> str:
        """
            builds the SPARQL endpoint for a given vocabulary
        Args:
            vocabulary (Vocabulary): The vocabulary

        Returns:
            str: the endpoint
        """
        return '{base}{name}/sparql'.format(base=self.url, name=vocabulary.get_name())

    def ping(self) -> bool:
        """
        Pings the Fuseki server, returns true/false if successful/unsuccessful

        Returns:
            bool: ping succesful
        """
        try:
            response = requests.get('{base}ping'.format(base=self.api_url))
            return response.ok
        except:
            return False

    def delete_vocabulary(self, vocabulary: Vocabulary) -> None:
        """
        Deletes a given vocabulary from fuseki

        Args:
            vocabulary (Vocabulary): The vocabulary that gets deleted

        Raises:
            ValueError: Vocabulary does not exist
            Exception: Vocabulary deleting failed for unknown reasons. Status code added as argument
        """
        response = requests.delete(
            '{base}datasets/{name}'.format(base=self.api_url, name=vocabulary.get_name()), auth=(user, password))

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ValueError('Vocabulary does not exist')

        if not response.ok:
            raise Exception('Deleting dataset failed', response.status_code)

    def create_vocabulary(self, vocabulary: Vocabulary) -> None:
        """
        Creates an empty and persisting vocabulary in Fuseki

        Args:
            vocabulary (Vocabulary): The vocabulary that gets created

        Raises:
            ValueError: Vocabulary name is already used
            Exception: Unexpected Error. Status code is in arguments
        """
        response = requests.post('{base}datasets?dbName={name}&dbType={type}'.format(
            base=self.api_url, name=vocabulary.get_name(), type='TDB2'), auth=(user, password))

        if response.status_code == HTTPStatus.CONFLICT:
            raise ValueError('This vocabulary name is already used')
        if not response.ok:
            raise Exception('Creating vocabulary failed.',
                            response.status_code)

    def restore_copy(self, vocabulary: Vocabulary, copy: Copy) -> None:
        """
            Creates a new vocabulary and restores the copy.
        Args:
            vocabulary (Vocabulary): The vocabulary that gets created
            copy (Copy): The copy of the other vocabulary

        Raises:
            ValueError: Vocabulary name is already used
            Exception: Unexpected error. Status code is in args
        """
        backup = open(copy.path, 'rb')
        response = requests.post('{base}datasets?dbName={name}&dbType={type}'.format(
            base=self.api_url, name=vocabulary.get_name(), type='TDB2'), files={'file': backup},  auth=(user, password))

        if response.status_code == HTTPStatus.CONFLICT:
            raise ValueError('This vocabulary name is already used')

        if not response.ok:
            raise Exception('Restoring Copy failed')

    def start_vocabulary_copy(self, vocabulary: Vocabulary) -> str:
        """
        Starts the backup process of the given vocabulary

        Args:
            vocabulary (Vocabulary): The vocabulary that gets backed up

        Raises:
            ValueError: Vocabulary does not exist
            Exception: Starting the backup failed unexpectedly

        Returns:
            str: taskID of the started backup task
        """
        response = requests.post('{base}backup/{name}'.format(
            base=self.api_url, name=vocabulary.get_name()), auth=(user, password))

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ValueError('Vocabulary does not exist')
        if not response.ok:
            raise Exception('Backing up vocabulary failed',
                            response.status_code)

        data = response.json()
        return data['taskId']

    def get_copy_tasks(self) -> List[Task]:
        """
            Gets all current tasks from Fuseki and returns the backup/copy tasks       

        Raises:
            Exception: Unexpected error while fetching tasks

        Returns:
            List[Task]: Backup tasks 
        """
        tasks: List[Task] = []
        response = requests.get('{base}tasks'.format(
            base=self.api_url), auth=(user, password))
        # check status code first
        if not response.ok:
            raise Exception('Failed to get tasks from Fuseki',
                            response.status_code)

        for task in response.json():
            tasks.append(Task(
                task.get('task'), task.get('taskId'), task.get('started'), task.get('finished'), task.get('success')))

        # only return the backup tasks
        tasks = [t for t in tasks if t.type == 'Backup']

        return tasks

    def __build_backup_path(self, filename: str) -> str:
        return os.path.join(self.backup_path, filename)

    def get_copy(self, task: Task, vocabulary: Vocabulary) -> Optional[Copy]:
        """
            Returns the copy object of a finished backup.

        Args:
            task (Task): Task that started the backup process
            vocabulary (Vocabulary): Vocabulary that got backed up

        Raises:
            ValueError: Backup is not finished or does not exist

        Returns:
            Optional[Copy]: Copy object of backup
        """
        response = requests.get('{base}backups-list'.format(
            base=self.api_url), auth=(user, password))

        backups = response.json()['backups']
        for backup in backups:
            # parse the vocabulary name from the backup filename
            name = '_'.join(backup[::-1].split('_', 2)[2:])[::-1]
            if name == vocabulary.get_name():
                return Copy(task, self.__build_backup_path(backup))
        raise ValueError('Backup could not be found')

    def query(self, vocabulary: Vocabulary, query: str) -> dict:
        """
        Sends SPARQL query to database and returns JSON dictionary

        Args:
            vocabulary (Vocabulary): Vocabulary that gets queried against
            query (str): SPARQL Query
        Returns:
            dict: JSON dictionary of the response
        """
        sparql = SPARQLWrapper('{base}{name}/sparql'.format(
            base=self.url, name=vocabulary.get_name()))

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results
