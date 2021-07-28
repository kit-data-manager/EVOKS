from django.db import models
from enum import Enum
from Profile.models import Profile


class Type(Enum):
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

    def __init__(self, receiver: Profile, message: str, type: Type) -> None:
        """Creates a new Notification instance.

        Args:
            receiver (Profile): User that receives the notification
            message (str): Notification message
            type (Type): Notification type
        """
        self.receiver = receiver
        self.message = message
        self.type = type
