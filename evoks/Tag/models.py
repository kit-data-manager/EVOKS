import datetime
from typing import Optional
from vocabularies.models import Vocabulary
from django.db import models
from django.db.models.deletion import CASCADE
import enum
import random

class Color(models.TextChoices):
    BLUE = 'blue'
    RED = 'red'
    GREEN = 'green'
    PINK = 'pink'
    YELLOW = 'yellow'
    PURPLE = 'purple'

class Tag(models.Model):
    """
    Class that models tags that users can leave on terms and vocabularies.
    Contains only the name of the tag and the post time.
    """

    max_name_length = 100
    name = models.CharField(max_length=max_name_length)  # type: str
    post_date = datetime.datetime.now
    vocabulary = models.ForeignKey(to='vocabularies.Vocabulary', on_delete=CASCADE, blank=True, null=True)
    term = models.ForeignKey(to='Term.Term', on_delete=CASCADE, blank=True, null=True)
    color = models.CharField(
        choices=Color.choices,
        default= random.choice(list(Color)),
        max_length=30
    )

    @classmethod
    def create(cls, name : str, vocabulary : Optional[Vocabulary]):
        tag = cls(name=name, vocabulary=vocabulary)
        tag.color = random.choice(list(Color))
        tag.save()
        print(tag.color)

        return tag

    #def __init__(self, name: str, vocabulary : Optional[Vocabulary]) -> None:
        #"""
        #Creates a new Tag instance

        #Args:
        #    name (str): The name of the tag
        #"""
        #self.name = name
        #self.color = random.choice(list(Color))
        #self.vocabulary = vocabulary
        #print(self.color)
