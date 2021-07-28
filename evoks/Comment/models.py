import datetime
from django.db import models
from Profile.models import Profile
from django.db.models.deletion import CASCADE, SET_NULL


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
    post_date = datetime.datetime.now

    def __init__(self, text: str) -> None:
        """
        Creates a new Comment instance

        Args:
            text (str): Comment text
        """
        self.text = text
