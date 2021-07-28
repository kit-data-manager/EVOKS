import datetime
from Term.models import Term
from vocabularies.models import Vocabulary
from django.db import models
from Profile.models import Profile
from django.db.models.deletion import CASCADE, SET_NULL
from typing import Optional


class Comment(models.Model):
    """
    Class that models comments that users can leave on terms and vocabularies.
    Contains the author, the date of creation, and the text of the comment.
    """

    max_text_length = 1000
    text = models.CharField(max_length=max_text_length)
    author = models.ForeignKey(to='Profile.Profile', on_delete=SET_NULL, blank=True, null=True)
    vocabulary = models.ForeignKey(to='vocabularies.Vocabulary', on_delete=CASCADE, blank=True, null=True)
    term = models.ForeignKey(to='Term.Term', on_delete=CASCADE, blank=True, null=True)
    post_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, text: str, author : Profile, vocabulary : Optional[Vocabulary], term : Optional[Term]) -> None:
        """
        Creates a new Comment instance

        Args:
            text (str): Comment text
        """
        comment = cls(text=text, author=author, vocabulary=vocabulary, term=term)
        comment.save()
        print(comment.post_date)
        return comment
