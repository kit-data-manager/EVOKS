import datetime
from django.db import models
from Profile.models import Profile 


class Comment(models.Model):

    max_text_length = 1000
    text = models.CharField(max_length=max_text_length)
    author = Profile
    post_date = datetime.datetime.now

    """
    Constructor for Comment. Takes only text as parameter.
    """
    def __init__(self, text):
        self.text = text

