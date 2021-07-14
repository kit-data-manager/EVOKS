from django.test import TestCase

from django.contrib.auth.models import Group
from GroupProfile.models import GroupProfile

from django.contrib.auth.models import User


class GroupProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Group.objects.create(name='hey')
        User.objects.create(username='tom', password='ok')

    def test_add(self):
        group = Group.objects.get(id=1)
        user = User.objects.get(name='hey')
        group.groupprofile.add_user(user)
        self.assertEquals(group.user_set.get(id=1),user)

    def test_add_counter(self):
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        self.assertEqual(group.groupprofile.size, 2)    

    
    