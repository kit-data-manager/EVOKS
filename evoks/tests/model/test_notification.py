from django.test import TestCase
from django.contrib.auth.models import User
from Notification.models import Notification
from Notification.models import Type


class NotificationTest(TestCase):
    """
    Test class for Notification.
    """

    @classmethod
    def setUp(cls):
        cls.receiver = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        cls.notification = Notification.create(receiver=cls.receiver.profile, message='error test', type=Type.ERROR)


    @classmethod
    def tearDown(cls):
        cls.receiver.delete()

    
    def test_create(self):
        """
        Test method for constructor. Checks if given parameters have been set correctly.
        """
        receiver = self.receiver
        notification = self.notification
        self.assertEquals(notification.receiver, receiver.profile)
        self.assertEquals(notification.message, 'error test')
        self.assertEquals(notification.type, Type.ERROR)

    
