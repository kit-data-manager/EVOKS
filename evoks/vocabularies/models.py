from django.db import models
from django.utils.datastructures import MultiValueDict
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm, get_perms
import Term.models
from django.core.mail import EmailMessage
from django.http import HttpRequest


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
# TODO delete vocabulary?


class Vocabulary(models.Model):
    name = models.CharField(max_length=30, unique=True)
    profiles = models.ManyToManyField(Profile, blank=True)
    description = models.CharField(max_length=30, default='', blank=True)
    term_count = models.IntegerField(default=0)
    groups = models.ManyToManyField(GroupProfile, blank=True)

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
    def create(cls, name: str, creator: Profile):
        # TODO return type
        # TODO Save creator in triple field
        # TODO fuseki create vocabulary
        vocabulary = cls(name=name)
        vocabulary.save()
        creator.user.save()
        vocabulary.profiles.add(creator)
        assign_perm('owner', creator.user, vocabulary)
        vocabulary.save()
        #fuseki_dev = Fuseki.objects.filter(port=3030)
        # fuseki_dev.create_vocabulary(vocabulary)
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

    def import_vocabulary(input: MultiValueDict) -> None:
        """Imports a Vocabulary

        Args:
            input ([type]): Vocabulary to import
        """
        # mögliche dateiformate: rdf/xml, Json-Ld, Turtle
        placeholder = 'sdf'

    def export_vocabulary(self, dataformat: Dataformat) -> None:
        """Sends the Vocabulary in the provided dataformat to the users email

        Args:
            dataformat (Enum): Desired dataformat
        """
        # TODO turn vocabulary into file in given format
        # TODO
        # TODO either has to take user as argument or sending email part handled in view
        vocab = 'placeholder'
        subject = '{0} Vocabulary in the {1} dataformat'.format(
            self.name, dataformat)
        body = 'Attached to this email is the requested Vocabulary...'
        email = EmailMessage(
            subject,
            body,
            'bob@example.com',
            'jhon@example.com'
        )
        formatstring = dataformat.lower()
        email.attach('{0}.{1}'.format(self.name, formatstring), vocab)
        email.send()

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

    # permission required participant or owner
    def add_term(self, name: str) -> None:
        """Adds a Term to the Vocabulary

        Args:
            name (str): Name of the Term
        """
        self.term_set.add(Term.models.Term.create(name=name))
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
        # fuseki_dev.buil_sparql_endpoint(self)
        placeholder = 123

    def create_field(url: str, type: str, content: str) -> str:
        """Creates a Triple Field on the Fuseki-Dev Instance

        Args:
            url (str): Url of the Triple
            type (str): Type of the Triple
            content (str): Content of the Triple

        Returns:
            str: [description]
        """
        placeholder = 123

    def delete_field(url: str) -> None:
        """Deletes a Triple Field on the Fuseki-Dev Instance

        Args:
            url (str): Url of the Triple
        """
        placeholder = 123

    def search(input: str):
        """Searches all Vocabularies for input. Vocabularies that contain input get put into a list and the list gets returned

        Args:
            input (str): Search string
        """
        placeholder = 123
