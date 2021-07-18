from typing import Type
from django.test import TestCase
from django.contrib.auth.models import User
from Notification.models import Notification
from Profile.models import Profile
from Notification.models import Type

class test_notification(TestCase):



    def test_init_(self):
        
        """Test method for constructor. Checks if given parameters has been set correctly.
        """
        
        sender = User.objects.create(username='ali', password='veli',email='aliveli@aliveli.com')
        profile = Profile(sender, sender.profile, True)
        profile2 = Profile(sender, sender.profile, False)
        obj = Notification(profile, 'error test', 'ERROR')
        self.assertEquals(obj.receiver, profile)
        self.assertEquals(obj.message, 'error test')
        self.assertEquals(obj.type, 'ERROR')
