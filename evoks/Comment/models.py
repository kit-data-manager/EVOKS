import datetime
from django.db import models
from Profile.models import Profile


class Comment(models.Model):
    """
    Class Comment. Has text, author and time, that comment has been created.
    """

    max_text_length = 1000
    text = models.CharField(max_length=max_text_length)
    author : Profile
    post_date = datetime.datetime.now

    def __init__(self, text : str) -> None:
        """
        Constructor for Comment. Takes only text as parameter.
        """
        self.text = text

