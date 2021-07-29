import datetime
from django.db import models


class Tag(models.Model):
    """
    Class that models tags that users can leave on terms and vocabularies.
    Contains only the name of the tag and the post time.
    """

    max_name_length = 100
    name = models.CharField(max_length=max_name_length)  # type: str
    post_date = datetime.datetime.now

    def __init__(self, name: str) -> None:
        """
        Creates a new Tag instance

        Args:
            name (str): The name of the tag
        """
        self.name = name
