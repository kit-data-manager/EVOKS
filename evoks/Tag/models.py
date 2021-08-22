import datetime
from typing import Optional
from vocabularies.models import Vocabulary
from Term.models import Term
from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
import random
from Profile.models import Profile

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
    name = models.CharField(max_length=max_name_length)
    post_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to='Profile.Profile', on_delete=SET_NULL, blank=True, null=True)
    vocabulary = models.ForeignKey(to='vocabularies.Vocabulary', on_delete=CASCADE, blank=True, null=True)
    term = models.ForeignKey(to='Term.Term', on_delete=CASCADE, blank=True, null=True)
    color = models.CharField(
        choices=Color.choices,
        default= random.choice(list(Color)),
        max_length=30
    )

    @classmethod
    def create(cls, name : str, author : Profile, vocabulary : Optional[Vocabulary], term : Optional[Term]):
        tag = cls(name=name, author=author, vocabulary=vocabulary, term=term)
        tag.color = random.choice(list(Color))
        tag.save()

        return tag

