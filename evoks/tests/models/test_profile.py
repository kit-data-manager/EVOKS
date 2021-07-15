from django.test import TestCase

from django.contrib.auth.models import User
from Profile.models import Profile


class ProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(username='jhon', password='ok',email='game111111@gmx.de')

    def test_verified_false(self):
        user = User.objects.get(username='jhon')
        self.assertFalse(user.profile.verified)

    def test_name(self):
        user = User.objects.get(username='jhon')
        user.profile.name = 'tom'
        self.assertEquals(user.profile.name, 'tom')

    def test_verified_true(self):
        user = User.objects.get(username='jhon')
        user.profile.verify()
        self.assertTrue(user.profile.verified)

    def test_verified_true(self):
        user = User.objects.get(username='jhon')
        user.profile.description='hi'
        self.assertAlmostEquals(user.profile.description, 'hi')

    def test_mail(self):
        user = User.objects.get(username='jhon')
        user.profile.export_userdata()
        print('mailed: '+user.email)
        self.assertTrue(True)

