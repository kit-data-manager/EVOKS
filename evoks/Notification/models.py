from django.db import models
from enum import Enum
from Profile.models import Profile
from django.db.models.deletion import CASCADE


class Type(models.TextChoices):
    """
    Enum for notification type.
    """
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'


class Notification(models.Model):
    """
    Class that models notifications that are sent to users.
    Contains a receiver, a message and a type.
    """

    receiver = models.ForeignKey(to='Profile.Profile', on_delete=CASCADE, blank=True, null=True)
    message = models.CharField(max_length=100, default='DEFAULT VALUE')
    type = models.CharField(
        choices=Type.choices, max_length=30, default=Type.ERROR)

    @classmethod
    def create(cls, receiver: Profile, message: str, type: Type) -> None:
        """
        Creates a new Comment instance

        Args:
            text (str): Comment text
        """
        notification = cls(receiver=receiver, message=message, type = type)
        notification.save()
        return notification
