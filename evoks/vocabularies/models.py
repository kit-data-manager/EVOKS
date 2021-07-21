from django.db import models
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum
from django.contrib.auth.models import Permission
#import Fuseki.fuseki


class State(enum.Enum):
    """State enum that represents the state of the Vocabulary

    Args:
        enum: Python Enum
    """
    DEV = 1
    REVIEW = 2
    LIVE = 3

#missing triple and searchable Interface TODO
#TODO delete vocabulary?
class Vocabulary(models.Model):
    name = models.CharField(max_length=30, unique=True)
    profiles = models.ManyToManyField(Profile, blank=True)
    description = models.CharField(max_length=30, default='', blank=True)
    term_count = models.IntegerField(default=0)
    groups = models.ManyToManyField(GroupProfile, blank=True)

    #many-to-one-fields belong in the 'one' models
    state = State

    class Meta:
        permissions = [
            ('owner', 'Owner'),
            ('participant', 'Participant'),
            ('spectator', 'Spectator'),
        ]

    @classmethod
    def create(cls, name : str, creator : Profile):
        #TODO return type
        #TODO set creator permission to owner
        #TODO Save creator in triple field
        #TODO fuseki create vocabulary
        vocabulary = cls(name=name)
        vocabulary.save()
        creator.user.save()
        #permission = Permission.objects.get(name='Owner')
        vocabulary.profiles.add(creator)
        #creator.user.user_permissions.add(permission)
        vocabulary.state = State.DEV
        vocabulary.save()
        #fuseki_dev = Fuseki.objects.filter(port=3030)
        #fuseki_dev.create_vocabulary(vocabulary)
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

    def import_vocabulary(input) -> None:
        """Imports a Vocabulary

        Args:
            input ([type]): Vocabulary to import
        """
        placeholder = 'sdf'

    def export_vocabulary(dataformat) -> None:
        """Sends the Vocabulary in the provided dataformat to the users email

        Args:
            dataformat (Enum): Desired dataformat
        """
        placeholder = '123'

    def set_live(self) -> None:
        """Sets the state to live and starts the migration process
        """
        if self.state == State.LIVE:
            raise ValueError('Vocabulary is already live')
        else:
            self.state = State.LIVE
            #thread?
            #fuseki.startvocabularycopy...
            #versionsnummer?
            #migration
            #skosmos

    def set_review(self) -> None:
        """Sets the state to review
        """
        if self.state == State.REVIEW:
            raise ValueError('Vocabulary is already in review')
        self.state = State.REVIEW
        #add to skosmos_dev
        #skosmos_dev = Skosmos.objects.filter(port=9080)
        #skosmos_dev.add_vocabulary(SkosmosConfig....)

    def set_dev(self) -> None:
        """Sets the state to dev
        """
        if self.state == State.DEV:
            raise ValueError('Vocabulary is already in development')
        self.state = State.DEV
        #remove from skosmos
        #skosmos_dev = Skosmos.objects.filter(port=9080)
        #skosmos_dev.delete_vocabulary(self.name)

    #permission required participant or owner
    def remove_term(self, name: str) -> None:
        """Removes a Term from the Vocabulary and deletes it

        Args:
            name (str): Name of the Term
        """
        #term = self.terms.objects.filter(name=name)
        #self.terms.remove(term)
        self.set_dev_if_live()
        #term.delete()

    #permission required participant or owner
    def add_term(self, name: str) -> None:
        """Adds a Term to the Vocabulary

        Args:
            name (str): Name of the Term
        """
        placeholder = '123'
        #self.terms.add(Term(self, name : str))
        #record user who added Term as contributor if not already done

    #permission required owner
    def add_profile(self, profile: Profile, permission: str) -> None:
        """Adds a User to the Vocabulary

        Args:
            profile (Profile): User to be added
            permission (Permission): Permission the User will have on the Vocabulary
        """
        self.profiles.add(profile)
        #self.profiles.get(profile).user.user_permissions.add(permission)

    #permission required owner
    def add_group(self, group: GroupProfile, permission: str) -> None:
        """Adds a group to the Vocabulary

        Args:
            group (GroupProfile): Group that is being added
            permission (str): Permission of the Group on the Vocabulary
        """
        #TODO Permission
        self.groups.add(group)
        #self.groups.get(group).group.permissions.add(permission)

    #permission required owner
    def remove_profile(self, profile: Profile) -> None:
        """Removes a User from the Vocabulary

        Args:
            profile (Profile): User that gets removed
        """
        self.profiles.remove(profile)
        #remove permissions?

    #permission required owner
    def remove_group(self, group: GroupProfile) -> None:
        """Removes a group from the Vocabulary

        Args:
            group (GroupProfile): Group that gets removed
        """
        self.groups.remove(group)
        #remove permissions?
