from django.db import models
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum
#from Fuseki.fuseki

class State(enum.Enum):
    dev = 1
    review = 2
    live = 3

# Create your models here.
#missing triple and searchable Interface
class Vocabulary(models.Model):
    description = models.CharField(max_length=30, default='')
    term_count = models.IntegerField(default=0)
    name = models.CharField(max_length=30, default='')

    def get_name(self):
        return self.name

    #on delete flage wrshl entweder SET_NULL oder SET_DEFAULT
    profiles = models.ManyToManyField(Profile, on_delete=models.SET_NULL)
    groups = models.ManyToManyField(GroupProfile, on_delete=models.SET_NULL)
    #many-to-one-fields belong in the 'one' models
    state = State

    #class Meta:
        #permissions = (('ownwer', 'Owner'),
                       #('participant', 'Participant'),
                       #('spectator', 'Spectator'))

    def __init__(self, name : str, creator : Profile) -> None:
        self.name = name

        self.profiles.add(creator)
        #missing: save creator in creator field
        #give user owner permissions
        

        self.state = 1

        #fuseki create_vocabulary?
    
    def test_if_live_vocabulary(self):
        if self.state is 3:
            self.state = 2
    
    def import_vocabulary(input):
        #stub
        placeholder = 'sdf'
        return None
    
    def export_vocabulary(dataformat):
        #stub
        placeholder='123'
    
    def set_live():
        state = 3
        #migration
    
    def set_review():
        state = 2
        #sumn else?
    
    def set_dev():
        state = 1
    
    def add_term(self, name : str):
        placeholder = '123'
        #self.terms.add(Term(self, name : str))
        #record user who added Term as contributor if not already done
    
    def add_profile(self, profile : Profile, permission : str):
        self.profiles.add(profile)
        #todo permissions
    
    def add_group(self, group : GroupProfile, permission : str):
        self.groups.add(group)

    def remove_term(self, name):
        term = self.terms.objects.filter(name=name)
        self.terms.remove(term)
        term.delete()
        self.test_if_live_vocabulary(self)
    
    def remove_profile(self, profile : Profile):
        self.profiles.remove(profile)
        #remove permissions
        #set from live to dev?
    
    def remove_group(self, group : GroupProfile):
        self.groups.remove(group)
        #remove permissions
        #set from live to dev?

    def get_name(self):
        return self.name
