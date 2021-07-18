from django.db import models
from enum import Enum
from Profile.models import Profile

class Type(Enum):
    """
    Enum for Notificationtype. Has 3 variables
    """
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'

class Notification(models.Model):
    """
    Notification Class. Has 3 attributes.
    """

    def __init__(self, receiver : Profile, message : str, type : Type) -> None:
        """Constructor for notification

        Args:
            receiver ([type]): User who receives notification
            message ([type]): Notification message
            type ([type]): Notification type
        """
        self.receiver = receiver
        self.message = message
        self.type = type

    