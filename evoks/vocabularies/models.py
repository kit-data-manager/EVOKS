from django.db import models
from django.utils.datastructures import MultiValueDict
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum
from guardian.shortcuts import assign_perm, remove_perm, get_perms
import Term.models
from django.contrib.postgres.fields import ArrayField
from django.http import HttpResponse, HttpRequest
import json
import requests
from django.conf import settings
from typing import List, Tuple


class State(models.TextChoices):
    """State enum that represents the state of the Vocabulary

    Args:
        enum: Python Enum
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

# missing triple and searchable Interface TODO


class Vocabulary(models.Model):
    name = models.SlugField(max_length=50, unique=True)
    profiles = models.ManyToManyField(Profile, blank=True)
    urispace = models.CharField(max_length=100, default='', blank=True)
    term_count = models.IntegerField(default=0)
    groups = models.ManyToManyField(GroupProfile, blank=True)
    prefixes = ArrayField(models.CharField(max_length=100), default=list)
    # many-to-one-fields belong in the 'one' models
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
        print(vocabulary.profiles)
        print(vocabulary.groups)
        creator.user.save()
        vocabulary.profiles.add(creator)
        assign_perm('owner', creator.user, vocabulary)
        vocabulary.save()
        fuseki_dev.create_vocabulary(vocabulary)
        return vocabulary

    def get_name(self) -> str:
        """Returns the name of the Vocabulary

        Returns:
            str: Name of the Vocabulary
        """
        return self.name

    def set_dev_if_live(self) -> None:
        """Sets Vocabulary state to DEV if it is LIVE
        """
        if self.state is State.LIVE:
            self.set_dev()

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
        
        #if not turtle different thing needed
        #n3: text/n3; charset=utf-8
        #nt: text/plain
        #rdf: application/rdf+xml
        #owl: application/rdf+xml
        #nq: application/n-quads
        #trig: application/trig
        #jsonld: application/ld+json
        headers = {'Content-Type': 'text/turtle;charset=utf-8'}
        r = requests.put('http://fuseki-dev:3030/{0}/data'.format(self.name), data=data, auth=(user, password), headers=headers)
        print(r)
 

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
            WHERE {
            <http://www.yso.fi/onto/yso/> ?predicate ?object
            }"""
        if dataformat == 'json':
            thing = fuseki_dev.query(self, query, 'json')
            file_content = json.dumps(thing, indent=4, sort_keys=True)
            response = HttpResponse(
                file_content, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export.json'
            return response
        elif dataformat == 'N3':
            thing = fuseki_dev.query(self, """
            DESCRIBE <http://www.yso.fi/onto/yso/> """, 'N3')
            file_content = thing.serialize(format='n3')
            response = HttpResponse(
                file_content, content_type='application/ttl')
            response['Content-Disposition'] = 'attachment; filename=export.ttl'
            return response
        elif dataformat == 'rdf/xml':
            thing = fuseki_dev.query(self, query, 'xml')
            file_content = thing.toprettyxml()
            response = HttpResponse(
                file_content, content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=export.xml'
            return response

    def set_live(self) -> None:
        """Sets the state to live and starts the migration process
        """
        if self.state != State.LIVE:
            self.state = State.LIVE
            # thread?
            # fuseki.startvocabularycopy...
            # versionsnummer?
            # migration
            # skosmos

    def set_review(self) -> None:
        """Sets the state to review
        """
        if self.state != State.REVIEW:
            self.state = State.REVIEW
        # add to skosmos_dev
        #skosmos_dev = Skosmos.objects.filter(port=9080)
        # skosmos_dev.add_vocabulary(SkosmosConfig....)

    def set_dev(self) -> None:
        """Sets the state to dev
        """
        if self.state != State.DEV:
            self.state = State.DEV
        # remove from skosmos
        #skosmos_dev = Skosmos.objects.filter(port=9080)
        # skosmos_dev.delete_vocabulary(self.name)

    # permission required participant or owner
    def remove_term(self, name: str) -> None:
        """Removes a Term from the Vocabulary and deletes it

        Args:
            name (str): Name of the Term
        """
        term = self.term_set.get(name=name)
        self.term_set.remove(term)
        self.set_dev_if_live()
        term.delete()
        self.term_count -= 1

    # permission required participant or owner
    def add_term(self, name: str) -> None:
        """Adds a Term to the Vocabulary

        Args:
            name (str): Name of the Term
        """
        self.term_set.add(Term.models.Term.create(name=name))
        self.term_count += 1
        # record user who added Term as contributor if not already done

    # permission required owner
    def add_profile(self, profile: Profile, permission: str) -> None:
        """Adds a User to the Vocabulary

        Args:
            profile (Profile): User to be added
            permission (Permission): Permission the User will have on the Vocabulary
        """
        self.profiles.add(profile)
        assign_perm(permission, profile.user, self)

    # permission required owner
    def add_group(self, group_profile: GroupProfile, permission: str) -> None:
        """Adds a group to the Vocabulary

        Args:
            group (GroupProfile): Group that is being added
            permission (str): Permission of the Group on the Vocabulary
        """
        self.groups.add(group_profile)
        assign_perm(permission, group_profile.group, self)

    # permission required owner
    def remove_profile(self, profile: Profile) -> None:
        """Removes a User from the Vocabulary

        Args:
            profile (Profile): User that gets removed
        """
        self.profiles.remove(profile)
        # currently removes all permissions user has :(
        # does this remove permissions given by groups?
        for key in get_perms(profile.user, self):
            remove_perm(key, profile.user, self)

    # permission required owner
    def remove_group(self, group_profile: GroupProfile) -> None:
        """Removes a group from the Vocabulary

        Args:
            group (GroupProfile): Group that gets removed
        """
        self.groups.remove(group_profile)
        for key in get_perms(group_profile.group, self):
            remove_perm(key, group_profile.group, self)

    def edit_field(url: str, type: str, content: str) -> None:
        """Edits a Triple field by using SPARQL Queries and the Fuseki-Dev Instance

        Args:
            url (str): Url of the Triple
            type (str): Typ of the Triple
            content (str): Content of the Triple
        """
        # fusek_dev.query(self,
        #   'DELETE { {0} {1} {2} }
        #   INSERT { {0} {1} {2} }
        #   WHERE
        #       { {0} {1} {2}
        #       }'.format(url, type, content)
        placeholder = 123

    def create_field(self, urispace: str, predicate: str, object: str) -> None:
        """Creates a Triple Field on the Fuseki-Dev Instance

        Args:
            url (str): Url of the Triple
            type (str): Type of the Triple
            content (str): Content of the Triple

        Returns:
            str: [description]
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.get_namespaces()
        query = self.prefixes_to_str(namespaces)

        # normalerweise ist {0} urispace aber ist noch nicht richtig initialisiert...
        query += 'INSERT DATA {{ {0} {1} {2} }}'.format(
            '<http://www.yso.fi/onto/yso/>', predicate, object)
        fuseki_dev.query(vocabulary=self, query=str(
            query), return_format='json', endpoint='update')

    def delete_field(url: str) -> None:
        """Deletes a Triple Field on the Fuseki-Dev Instance

        Args:
            url (str): Url of the Triple
        """
        # fuseki_dev.query(self,
        #   'DELETE DATA
        #   {
        #       {0} {1} {2}  ;
        #   }'.format(url, type, content)
        placeholder = 123

    def search(input: str):
        """Searches all Vocabularies for input. Vocabularies that contain input get put into a list and the list gets returned

        Args:
            input (str): Search string
        """
        placeholder = 123
