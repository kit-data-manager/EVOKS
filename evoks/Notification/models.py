from django.db import models
from enum import Enum
from Profile.models import Profile

class Type(Enum):
    """Enum for Type
    """
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'

class Notification(models.Model):

    receiver = Profile
    message = str
    type = Type

    def __init__(self, receiver, message, type):
        """Constructor for notification

        Args:
            receiver ([type]): User who receives notification
            message ([type]): Notification message
            type ([type]): Notification type
        """
        self.receiver = receiver
        self.message = message
        self.type = type

    