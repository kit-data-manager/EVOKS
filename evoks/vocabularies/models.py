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
from skosify import skosify
import logging
from django.core.files.storage import FileSystemStorage
from rdflib import Graph
import os
from django.utils.crypto import get_random_string
from tempfile import NamedTemporaryFile
from time import sleep
from rdflib.namespace import _is_valid_uri


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


def find_urispace(subjects):

    prefix = subjects[0]
    for word in subjects:
        if len(prefix) > len(word):
            prefix, word = word, prefix

        while len(prefix) > 0:
            if word[:len(prefix)] == prefix:
                break
            else:
                prefix = prefix[:-1]
    return prefix


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
        from evoks.fuseki import fuseki_dev

        user = settings.FUSEKI_USER
        password = settings.FUSEKI_PASSWORD

        file = input.open()
        data = file.read()
        extension = file.name.split(".")[-1]
        if not any(ext == extension for ext in ['rdf', 'jsonld', 'ttl']):
            raise ValueError(
                'invalid file ending. allowed files: rdf, jsonld, ttl')
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        # if its jsonld we just convert it to turtle and continue as if nothing happend
        if extension == 'jsonld':
            data = bytes(Graph().parse(
                data=data, format='json-ld').serialize(format='turtle'), encoding='raw_unicode_escape')
            extension = 'ttl'

        with NamedTemporaryFile(suffix='.'+extension) as tmp:

            tmp.write(data)
            tmp.seek(0)
            try:
                voc = skosify(tmp.name, label='iptc')
                voc.serialize(destination=tmp.name, format='xml')
            except:
                raise ValueError('invalid format. skosify failed')

            if extension == 'rdf':
                content_type = 'application/rdf+xml'
            elif extension == 'ttl':
                content_type = 'text/turtle'

            headers = {'Content-Type': content_type}
            r = requests.put('http://fuseki-dev:3030/{0}/data'.format(
                self.name), data=tmp.read(), auth=(user, password), headers=headers)
            if not r.ok:
                raise ValueError('import failed', r.status_code)

            query = """
                SELECT DISTINCT ?s
                WHERE {
                ?s ?p ?o
                }
            """
            result = fuseki_dev.query(self, query, 'json')
            subjects: List[str] = []
            for x in result['results']['bindings']:
                uri = x['s']['value']
                subjects.append(uri)

            new_urispace = find_urispace(subjects)

            for x in result['results']['bindings']:
                try:

                    uri = x['s']['value']
                    id = uri.split(new_urispace)[1]
                    base = id.replace('/', '_')
                    name = base
                    i = 1
                    while Term.objects.filter(name=name).exists():
                        name = '{0}_{1}'.format(base, i)
                        i += 1

                    self.add_term(name, id)

                except Exception as e:
                    print(e)

            if self.urispace != '':
                last_char = new_urispace[-1]
                last_char_new = self.urispace[-1]
                if last_char == '/' or last_char == '#' and last_char_new != '/' and last_char_new != '#':
                    self.urispace += '/'
                    self.save()
                query = """
                DELETE
                {{ ?oldIRI ?p ?o }}
                INSERT
                {{ ?newIRI ?p ?o }}
                WHERE
                {{
                    ?oldIRI ?p ?o .
                    BIND(
                        IRI(CONCAT("{new_urispace}",
                            SUBSTR(STR(?oldIRI), STRLEN(STR("{urispace}"))+1 ) 
                    )) AS ?newIRI
                    )

                    FILTER(strstarts(str(?oldIRI), "{urispace}"))
                }}""".format(new_urispace=self.urispace, urispace=new_urispace)
                fuseki_dev.query(self, query, 'xml', 'update')

            if self.urispace == '':
                self.urispace = new_urispace
                self.save()

    def validate_prefixes(self, prefixes: List):
        from vocabularies.views import uri_validator

        for key in prefixes:
            split = key.split()
            if not len(split) == 3:
                return False
            elif not (split[0] == "PREFIX" and split[1].endswith(":") and split[1].endswith(":") and split[2].startswith("<") and split[2].endswith(">")):
                return False
            elif not uri_validator(split[2][1:-1]):
                return False
            elif not _is_valid_uri(split[2][1:-1]):
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

        namespaces = [('skos', 'http://www.w3.org/2004/02/skos/core#'),
                      ('dc', 'http://purl.org/dc/elements/1.1/'),
                      ('dct', 'http://purl.org/dc/terms/')
                      ]

        v_prefixes = self.split_prefixes(self.convert_prefixes(self.prefixes))
        for prefix in v_prefixes:
            namespaces.append(prefix)

        for short, uri in p.namespaces():
            namespaces.append((short, uri.toPython()))

        return namespaces

    def convert_prefix(self, object_string: str) -> Tuple[bool, str]:
        """Converts a string like skos:prefLabel to https://www.w3.org/2009/08/skos-reference/skos.html#prefLabel

        Args:
            object_string (str): string to be converted

        Returns:
            Tuple[bool, str]: True if valid, str is complete uri
        """
        from vocabularies.views import uri_validator

        valid = False
        namespaces = self.get_namespaces()
        for p, u in namespaces:
            prefix = '{0}:'.format(p)
            if object_string.startswith(prefix):
                relative_uri = object_string.split(prefix)[1]
                if not uri_validator(u + relative_uri):
                    return (False, '')
                else:
                    object_string = u + relative_uri
                    valid = True
            break
        return (valid, object_string)

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
            content_type = 'application/json-ld'
            content_disposition = 'attachment; filename={0}.jsonld'.format(
                self.name)
        elif dataformat == 'turtle':
            thing = fuseki_dev.query(self, """
            DESCRIBE <{0}> """.format(urispace), 'xml')
            file_content = thing.serialize(format='n3')
            content_type = 'application/ttl'
            content_disposition = 'attachment; filename={0}.ttl'.format(
                self.name)
        elif dataformat == 'rdf+xml':
            thing = fuseki_dev.query(self, query, 'xml')
            file_content = thing.toprettyxml()
            content_type = 'application/rdf+xml'
            content_disposition = 'attachment; filename={0}.rdf'.format(
                self.name)

        export = {
            'file_content': file_content,
            'content_type': content_type,
            'content_disposition': content_disposition
        }
        return export

    def get_languages(self) -> List[str]:
        """Returns the languages of the vocabulary"""
        from evoks.fuseki import fuseki_dev
        query = """
            SELECT DISTINCT (lang(?obj) as ?lang) WHERE {
            ?sub ?pred ?obj
            }"""
        res = fuseki_dev.query(self, query, 'json')
        languages: List[str] = []
        for x in res['results']['bindings']:
            if 'lang' in x and x['lang']['value'] != '':
                languages.append(x['lang']['value'])

        return languages

    def get_top_language(self) -> str:
        """Returns the most used language"""
        from evoks.fuseki import fuseki_dev

        languages = self.get_languages()
        languages_str = ', '.join(f'"{w}"' for w in languages)
        query = """
            PREFIX  skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT  ?lang ?prop (COUNT(?label) AS ?count)
            WHERE
            {{ {{ VALUES ?type {{ skos:Concept }}
                VALUES ?prop {{ skos:prefLabel }}
                ?conc  a      ?type ;
                        ?prop  ?label
                BIND(lang(?label) AS ?lang)
                    FILTER ( ?lang IN ({0}) )
                }}
            }}
            GROUP BY ?lang ?prop ?type
            """.format(languages_str)
        res = fuseki_dev.query(self, query, 'json')
        max = 0
        max_lang = ''
        for x in res['results']['bindings']:
            lang = x['lang']['value']
            count = int(x['count']['value'])
            if count > max:
                max = count
                max_lang = lang
        return max_lang

    def set_live(self) -> None:
        """Sets the state to live and starts the migration process
        """
        from Migration.migration_context import MigrationContext
        from Migration.backup_migration_strategy import BackupMigrationStrategy
        from evoks.fuseki import fuseki_live

        if self.state != State.LIVE:

            if self.state == State.REVIEW:
                skosmos_dev.delete_vocabulary(self.name)

            context = MigrationContext(BackupMigrationStrategy())
            context.start(self)

            self.version += 1

            self.state = State.LIVE
            self.save()

    def set_review(self) -> None:
        """Sets the state to review
        """
        from evoks.fuseki import fuseki_dev, fuseki_live
        top_lang = self.get_top_language()
        languages = self.get_languages()
        if self.state != State.REVIEW:
            config = SkosmosVocabularyConfig('cat_general', self.name, self.name_with_version(
            ), languages, fuseki_dev.build_sparql_endpoint(self), self.urispace, top_lang)
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

    # permission required participant or owner
    def add_term(self, name: str, uri: str) -> None:
        """Adds a Term to the Vocabulary

        Args:
            name (str): Name of the Term
        """
        self.term_set.add(Term.create(name=name, uri=uri))
        self.term_count += 1
        if self.state == State.LIVE:
            self.set_dev()
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

    def change_profile_perm(self, profile: Profile, newperm: str) -> None:
        """Changes Permission of the given Profile to the given permission

        Args:
            profile (Profile): given profile
            newperm (str): new permission of the profile
        """
        # remove old perms
        for key in get_perms(profile.user, self):
            remove_perm(key, profile.user, self)
        # assign new perm
        assign_perm(newperm, profile.user, self)

    def change_group_perm(self, group_profile: GroupProfile, newperm: str) -> None:
        """Changes Permission of the given Profile to the given permission

        Args:
            profile (Profile): given profile
            newperm (str): new permission of the profile
        """
        # remove old perms
        for key in get_perms(group_profile.group, self):
            remove_perm(key, group_profile.group, self)
        # assign new perm
        assign_perm(newperm, group_profile.group, self)

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
        if self.state == State.LIVE:
            self.set_dev()

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
        if self.state == State.LIVE:
            self.set_dev()

    def delete_field(self, predicate: str, object: str) -> None:
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
        if self.state == State.LIVE:
            self.set_dev()
