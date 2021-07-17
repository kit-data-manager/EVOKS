from django.db import models
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum
from django.contrib.auth.models import Permission
#import Fuseki.fuseki


class State(enum.Enum):
    """State enum that represents the state of the Vocabulary

    Args:
        enum ([Enum): Python Enum
    """
    dev = 1
    review = 2
    live = 3

# Create your models here.
#missing triple and searchable Interface TODO


class Vocabulary(models.Model):
    name = models.CharField(max_length=30, default='', unique=True)
    profiles = models.ManyToManyField(Profile, blank=True)
    description = models.CharField(max_length=30, default='', blank=True)
    term_count = models.IntegerField(default=0)

    #many to many field hat kein on_delete
    groups = models.ManyToManyField(GroupProfile, blank=True)
    #many-to-one-fields belong in the 'one' models
    state = State

    class Meta:
        permissions = (('ownwer', 'Owner'),
                       ('participant', 'Participant'),
                       ('spectator', 'Spectator'))

    #def __init__(self, name: str, creator: Profile) -> None:
        """Creates a new Vocabulary Object

        Args:
            name (str): Name of the Vocabulary
            creator (Profile): User that created the Vocabulary
        """
        #super().__init__(name, creator)
        #self.name = name
        #vocabulary = self.model(name=name)
        #vocabulary.save()
        #creator.user.save()
        #self.save()
        #self.profiles.add(creator)
        #self.profiles.get(creator).user.user_permissions.add('owner')
        #missing: save creator in creator field TODO

        #self.state = 1

        #fuseki_dev = Fuseki.objects.filter(port=3030)
        #fuseki_dev.create_vocabulary(self)

    def create_vocabulary(name : str, creator : Profile) -> None:
        vocabulary = Vocabulary.objects.create(name=name)
        vocabulary.save()
        creator.user.save()
        print(Permission.objects.all())
        permission = Permission.objects.get(name=('owner', 'Owner'))
        vocabulary.profiles.add(creator)
        vocabulary.profiles.get(user=creator.user).user.user_permissions.add(permission)

    def get_name(self) -> str:
        return self.name

    def set_dev_if_live(self) -> None:
        """Tests if Vocabulary is live and sets it to dev
        """
        if self.state == 3:
            self.state = 2

    def import_vocabulary(input) -> None:
        """Imports a Vocabulary

        Args:
            input ([type]): Vocabulary to import
        """
        #stub
        placeholder = 'sdf'

    def export_vocabulary(dataformat) -> None:
        """Sends the Vocabulary in the provided dataformat to the users email

        Args:
            dataformat (Enum): Desired dataformat
        """
        #stub
        placeholder = '123'

    def set_live(self) -> None:
        """Sets the state to live and starts the migration process
        """
        if self.state == 3:
            raise ValueError('Vocabulary is already live')
        else:
            state = 3
            #thread?
            #fuseki.startvocabularycopy...
            #versionsnummer?
            #migration

    def set_review() -> None:
        """Sets the state to review
        """
        state = 2
        #sumn else?

    def set_dev() -> None:
        """Sets the state to dev
        """
        state = 1

    #permission required participant or owner
    def remove_term(self, name: str) -> None:
        """Removes a Term from the Vocabulary and deletes it

        Args:
            name (str): Name of the Term
        """
        term = self.terms.objects.filter(name=name)
        self.terms.remove(term)
        self.set_dev_if_live(self)
        term.delete()

    #permission required participant or owner

    def add_term(self, name: str) -> None:
        """Adds a Term to the Vocabulary

        Args:
            name (str): Name of the Term
        """
        placeholder = '123'
        #check permission?
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
        self.profiles.get(profile).user.user_permissions.add(permission)

    #permission required owner
    def add_group(self, group: GroupProfile, permission: str) -> None:
        self.groups.add(group)
        self.groups.get(group).permissions.add(permission)

    #permission required owner
    #can you remove urself?
    def remove_profile(self, profile: Profile) -> None:
        self.profiles.remove(profile)
        #remove permissions
        #set from live to dev?

    #permission required owner
    def remove_group(self, group: GroupProfile) -> None:
        self.groups.remove(group)
        #remove permissions
        #set from live to dev?
