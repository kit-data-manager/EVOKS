from django.db import models
from Profile.models import Profile
from GroupProfile.models import GroupProfile
import enum

class State(enum.Enum):
    dev = 1
    review = 2
    live = 3

# Create your models here.
#missing triple and searchable Interface
class Vocabulary(models.Model):
    description = models.CharField(max_length=30)
    term_count = models.IntegerField()
    #on delete flage wrshl entweder SET_NULL oder SET_DEFAULT
    profiles = models.ManyToManyField(Profile, on_delete=models.SET_NULL)
    groups = models.ManyToManyField(GroupProfile, on_delete=models.SET_NULL)
    #many-to-one-fields belong in the 'one' models
    state = State

    class Meta:
        permissions = (('ownwer', 'Owner'),
                       ('participant', 'Participant'),
                       ('spectator', 'Spectator'))

    def __init__(self, title):
        #set title
        #save user as creator
        #give user owner permissions
        #state = dev
    
    def import_vocabulary(input):
        #stub
        placeholder = 'sdf'
        return None
    
    def export_vocabulary(dataformat):
        #stub
    
    def set_live():
        #stub
    
    def set_review():
        #stub
    
    def set_dev():
        #stub
    
    def add_term(name):
        #stub
    
    def add_profile(profile : Profile, permission):
        #stub
    
    def add_group(group : GroupProfile, permission):
        #stub

    def remove_term(name):
        #stub
    
    def remove_profile(profile : Profile):
        #stub
    
    def remove_group(group : GroupProfile):
        #stub


