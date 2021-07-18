import datetime
from django.db import models


class Tag(models.Model):
    """
    Class Tag. Has name and time, that tag has been created.
    """

    max_name_length = 100
    name = models.CharField(max_length=max_name_length)  # type: str
    post_date = datetime.datetime.now

    def __init__(self, name : str) -> None:
        """
        Consturctor for Tag. Takes only name as parameter.
        """
        self.name = name
