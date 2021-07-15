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
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        self.assertEquals(group.user_set.get(username='tom'), user)

    def test_add_counter(self):
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        self.assertEqual(group.groupprofile.size, 2)

    def test_remove_counter(self):
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        group.groupprofile.remove_user(user)
        self.assertEqual(group.groupprofile.size, 1)

    def test_remove_counter_zero(self):
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        group.groupprofile.size=0
        group.groupprofile.remove_user(user)
        self.assertFalse(Group.objects.filter(id=group.id).exists())