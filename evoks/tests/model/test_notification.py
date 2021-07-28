from typing import Type
from django.test import TestCase
from django.contrib.auth.models import User
from Notification.models import Notification
from Profile.models import Profile
from Notification.models import Type


class test_notification(TestCase):
    """
    Test class for Notification.
    """

    def test_init_(self):
        """
        Test method for constructor. Checks if given parameters have been set correctly.
        """

        sender = User.objects.create(
            username='ali', password='veli', email='aliveli@aliveli.com')
        profile = Profile(sender, sender.profile, True)
        obj = Notification(profile, 'error test', 'ERROR')
        self.assertEquals(obj.receiver, profile)
        self.assertEquals(obj.message, 'error test')
        self.assertEquals(obj.type, 'ERROR')
