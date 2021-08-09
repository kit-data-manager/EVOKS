from django.test import TestCase

from django.contrib.auth.models import User
from Profile.models import Profile
from django.conf import settings
from unittest import skip


class ProfileTest(TestCase):
    @classmethod
    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user=User.objects.create(username='jhon', password='ok',
                            email='example@example.de')
    @classmethod
    def tearDown(self):
        self.user.delete()

    def test_name(self):
        self.user.profile.name = 'tom'
        self.assertEquals(self.user.profile.name, 'tom')

    def test_verified_false(self):
        self.assertFalse(self.user.profile.verified)

    def test_verified_true(self):
        self.user.profile.verify()
        self.assertTrue(self.user.profile.verified)
        
    def test_description(self):
        self.user.profile.description = 'hi'
        self.user.save()
        self.assertEquals(self.user.profile.description, 'hi')


    
