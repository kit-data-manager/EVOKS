from Skosmos.skosmos_vocabulary_config import SkosmosVocabularyConfig
from django.db import models
from django.utils.datastructures import MultiValueDict
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from Term.models import Term
from django.contrib.postgres.fields import ArrayField
from django.http import HttpResponse, HttpRequest
import json
import requests
from django.conf import settings
from typing import List, Tuple
from evoks.skosmos import skosmos_dev, skosmos_live


class State(models.TextChoices):
    """State TextChoices that represent the state of the Vocabulary

    Args:
        models (TextChoices): possible states of a vocabulary
    """
    DEV = 'Development'
    REVIEW = 'Review'
    LIVE = 'Live'


class Dataformat(enum.Enum):
    """Dataformat enum represents the different kinds of Format that are selectable when downloading a Vocabulary

    Args:
        enum: Python Enum
    """
    RDFXML = 1
    JSONLD = 2
    TURTLE = 3



class Vocabulary(models.Model):
    name = models.SlugField(max_length=50, unique=True)
    profiles = models.ManyToManyField(Profile, blank=True)
    urispace = models.CharField(max_length=100, default='', blank=True)
    term_count = models.IntegerField(default=0)
    groups = models.ManyToManyField(GroupProfile, blank=True)
    prefixes = ArrayField(models.CharField(max_length=100), default=list)
    version = models.IntegerField(default=1)
    state = models.CharField(
        choices=State.choices,
        default=State.DEV,
        max_length=30
    )

    class Meta:
        permissions = [
            ('owner', 'Owner'),
            ('participant', 'Participant'),
            ('spectator', 'Spectator'),
        ]

    @classmethod
    def create(cls, name: str, urispace: str, creator: Profile):
        from evoks.fuseki import fuseki_dev
        # TODO return type
        # TODO Save creator in triple field
        vocabulary = cls(name=name, urispace=urispace)
        vocabulary.save()
        creator.user.save()
        vocabulary.profiles.add(creator)
        assign_perm('owner', creator.user, vocabulary)
        vocabulary.save()
        fuseki_dev.create_vocabulary(vocabulary)
        return vocabulary

    def name_with_version(self) -> str:
        """Returns the name of the Vocabulary with the version

        Returns:
            str: name-version
        """
        return '{0}-{1}'.format(self.name, self.version)

    def get_name(self) -> str:
        """Returns the name of the Vocabulary

        Returns:
            str: Name of the Vocabulary
        """
        return self.name

    def import_vocabulary(self, input) -> None:
        """Imports a Vocabulary

        Args:
            input (): Vocabulary to import
        """
        # TODO mögliche dateiformate: ?
        from evoks.fuseki import fuseki_dev


        user = settings.FUSEKI_USER
        password = settings.FUSEKI_PASSWORD

        data = input.open().read()

        # if not turtle different thing needed
        #n3: text/n3; charset=utf-8
        #nt: text/plain
        #rdf: application/rdf+xml
        #owl: application/rdf+xml
        #nq: application/n-quads
        #trig: application/trig
        #jsonld: application/ld+json
        headers = {'Content-Type': 'text/turtle;charset=utf-8'}
        r = requests.put('http://fuseki-dev:3030/{0}/data'.format(
            self.name), data=data, auth=(user, password), headers=headers)
        if not r.ok:
            raise ValueError()

        query = """        
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT DISTINCT ?s
            WHERE {{
                ?s skos:prefLabel ?o .
            FILTER (strstarts(str(?s), '{0}'))
            }}
        """.format(self.urispace)
        result = fuseki_dev.query(self, query, 'json')

        for x in result['results']['bindings']:
            try:
                uri = x['s']['value']
                id = uri.split(self.urispace)[1]
                self.add_term(id)
            except Exception as e:
                print(e)


    def validate_prefixes(self, prefixes : List):
        for key in prefixes:
            split = key.split()
            if not len(split) == 3:
                return False
            elif not (split[0] == "PREFIX" and split[1].endswith(":") and  split[1].endswith(":") and split[2].startswith("<") and split[2].endswith(">")):
                return False     
        return True

    def get_namespaces(self) -> List[Tuple[str, str]]:
        """Returns list of namespaces from fuseki and the prefixes tab

        Args:
            vocabulary (Vocabulary): vocabulary to get namespaces from

        Returns:
            List[Tuple[str, str]]: [description]
        """
        from evoks.fuseki import fuseki_dev
        p = fuseki_dev.query(
            self, """DESCRIBE <{0}>""".format(self.urispace), 'xml')

        namespaces = []

        v_prefixes = self.split_prefixes(self.convert_prefixes(self.prefixes))
        for prefix in v_prefixes:
            namespaces.append(prefix)

        for short, uri in p.namespaces():
            namespaces.append((short, uri.toPython()))

        return namespaces


    def prefixes_to_str(self, namespaces: List[Tuple[str, str]]) -> str:
        prefix_list: List[str] = []
        for k, value in namespaces:
            prefix_string = 'prefix {0}: <{1}>'.format(k, value)
            prefix_list.append(prefix_string)
        query = '\n'.join(prefix_list)
        return query


    def split_prefixes(self, prefixes: List[str]):
        splitted: List[Tuple[str, str]] = []
        for prefix in prefixes:
            parts = prefix.split()
            splitted.append((parts[1], parts[2][1:-1]))
        return splitted


    def convert_prefixes(self, prefixes: List[str]):
        """Turns a list of prefixes from this format: @prefix allars:   <http://www.yso.fi/onto/allars/> . to PREFIX allars <http://www.yso.fi/onto/allars/>

        Args:
            prefixes (List[str]): List of prefixes

        Returns:
            List[str]: List of converted prefixes
        """
        converted: List[str] = []
        for prefix in prefixes:
            parts = prefix.split()
            converted.append('PREFIX {prefix} {url}'.format(
                prefix=parts[1][:-1], url=parts[2]))

        return converted


    def export_vocabulary(self, dataformat: str) -> None:
        """Sends the Vocabulary in the provided dataformat to the users email

        Args:
            dataformat (Enum): Desired dataformat
        """
        # TODO put urispace in there
        from evoks.fuseki import fuseki_dev
        urispace = self.urispace
        query = """
            SELECT ?subject ?predicate ?object
            WHERE {{
            <{0}> ?predicate ?object
            }}""".format(urispace)
        if dataformat == 'json-ld':
            thing = fuseki_dev.query(self, """
            DESCRIBE <{0}> """.format(urispace), 'xml')
            file_content = thing.serialize(format='json-ld')
            content_type='application/json-ld'
            content_disposition = 'attachment; filename={0}.jsonld'.format(self.name)
        elif dataformat == 'turtle':
            thing = fuseki_dev.query(self, """
            DESCRIBE <{0}> """.format(urispace), 'xml')
            file_content = thing.serialize(format='n3')
            content_type='application/ttl'
            content_disposition = 'attachment; filename={0}.ttl'.format(self.name)
        elif dataformat == 'rdf+xml':
            thing = fuseki_dev.query(self, query, 'xml')
            file_content = thing.toprettyxml()
            content_type='application/rdf+xml'
            content_disposition = 'attachment; filename={0}.rdf'.format(self.name)

        export = {
            'file_content' : file_content,
            'content_type' : content_type,
            'content_disposition' : content_disposition
        }
        return export


    def set_live(self) -> None:
        """Sets the state to live and starts the migration process
        """
        from Migration.migration_context import MigrationContext
        from Migration.backup_migration_strategy import BackupMigrationStrategy
        from evoks.fuseki import fuseki_live

   
        if self.state != State.LIVE:

            if self.state == State.REVIEW:
                skosmos_dev.delete_vocabulary(self.name)

            #if self.version > 1:
            #    skosmos_live.delete_vocabulary(self.name)
            #    fuseki_live.delete_vocabulary(self)

            context = MigrationContext(BackupMigrationStrategy())
            context.start(self)
            self.state = State.LIVE
            self.version += 1
            self.save()

    def set_review(self) -> None:
        """Sets the state to review
        """
        from evoks.fuseki import fuseki_dev, fuseki_live

        
        if self.state != State.REVIEW:
            config = SkosmosVocabularyConfig('cat_general', self.name_with_version(), self.name, [
                                             'en'], fuseki_dev.build_sparql_endpoint(self), self.urispace, 'en')
            skosmos_dev.add_vocabulary(config)
            self.state = State.REVIEW
            self.save()


    def set_dev(self) -> None:
        """Sets the state to dev
        """
        from evoks.fuseki import fuseki_dev, fuseki_live

        if self.state != State.DEV:
            # if we are in review, just remove from skosmos dev
            if self.state == State.REVIEW:
                skosmos_dev.delete_vocabulary(self.name)
            # if we are in live, remove from skosmos live and fuseki live
            self.state = State.DEV
            self.save()

    def remove_term(self, name: str) -> None:
        """Removes a Term from the Vocabulary and deletes it

        Args:
            name (str): Name of the Term
        """
        term = self.term_set.get(name=name)
        self.term_set.remove(term)
        if self.state == State.LIVE:
            self.set_dev()
        term.delete()
        self.term_count -= 1

    def add_term(self, name: str) -> None:
        """Adds a Term to the Vocabulary

        Args:
            name (str): Name of the Term
        """
        self.term_set.add(Term.create(name=name))
        self.term_count += 1
        # record user who added Term as contributor if not already done

    def add_profile(self, profile: Profile, permission: str) -> None:
        """Adds a User to the Vocabulary

        Args:
            profile (Profile): User to be added
            permission (str): Permission the User will have on the Vocabulary
        """
        self.profiles.add(profile)
        assign_perm(permission, profile.user, self)

    def add_group(self, group_profile: GroupProfile, permission: str) -> None:
        """Adds a group to the Vocabulary

        Args:
            group (GroupProfile): Group that is being added
            permission (str): Permission of the Group on the Vocabulary
        """
        self.groups.add(group_profile)
        assign_perm(permission, group_profile.group, self)

    def remove_profile(self, profile: Profile) -> None:
        """Removes a User from the Vocabulary

        Args:
            profile (Profile): User that gets removed
        """
        self.profiles.remove(profile)
        for key in get_perms(profile.user, self):
            remove_perm(key, profile.user, self)

    def remove_group(self, group_profile: GroupProfile) -> None:
        """Removes a group from the Vocabulary

        Args:
            group (GroupProfile): Group that gets removed
        """
        self.groups.remove(group_profile)
        for key in get_perms(group_profile.group, self):
            remove_perm(key, group_profile.group, self)

    def edit_field(self, predicate: str, old_object: str, new_object: str) -> None:
        """Replaces the object of a triple field with a new object, by using SPARQL Queries and the Fuseki-Dev Instance

        Args:
            predicate (str): Predicate of the triple
            old_object (str): Old object of the triple
            new_object (str): New object of the triple
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.get_namespaces()
        query = self.prefixes_to_str(namespaces)
        query += """
        DELETE {{ <{urispace}> <{predicate}> {old_object} }}
        INSERT {{ <{urispace}> <{predicate}> {new_object} }}
        WHERE
        {{ <{urispace}> <{predicate}> {old_object} }}
        """.format(new_object=new_object, urispace=self.urispace, predicate=predicate, old_object=old_object)
        fuseki_dev.query(
            self, query, 'xml', 'update')

    def create_field(self, urispace: str, predicate: str, object: str) -> None:
        """Creates a Triple Field on the Fuseki-Dev Instance

        Args:
            urispace (str): urispace of the vocabulary and subject of the triple
            predicate (str): predicate of the triple
            object (str): object of the triple
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.get_namespaces()
        query = self.prefixes_to_str(namespaces)

        query += 'INSERT DATA {{ {0} {1} {2} }}'.format(
            urispace, predicate, object)
        fuseki_dev.query(vocabulary=self, query=str(
            query), return_format='json', endpoint='update')

    def delete_field(self, predicate : str, object : str) -> None:
        """Deletes a Triple Field of the vocabulary on the Fuseki-Dev Instance

        Args:
            predicate (str): Predicate of the triple
            object (str): Object of the triple
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.get_namespaces()
        query = self.prefixes_to_str(namespaces)
        query += """
        DELETE DATA
        {{ <{urispace}> <{predicate}> {object} }}
        """.format(urispace=self.urispace, predicate=predicate, object=object)
        fuseki_dev.query(
            self, query, 'xml', 'update')

    def search(input: str):
        """Searches all Vocabularies for input. Vocabularies that contain input get put into a list and the list gets returned

        Args:
            input (str): Search string
        """
        placeholder = 123
