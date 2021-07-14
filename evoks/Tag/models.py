import datetime
from django.db import models

class Tag(models.Model):

    max_name_length = 100
    name = models.CharField(max_length=max_name_length)
    post_date = datetime.datetime.now

    """
    Consturctor for Tag. Takes only name as parameter.
    """
    def __init__(self, name):

        self.name = name
        
