from django.test import TestCase
from django.contrib.auth.models import Group
from GroupProfile.models import GroupProfile
from django.contrib.auth.models import User, Group


class GroupProfileTest(TestCase):
    """Test class for Groupprofile

    Args:
        TestCase ([type]): [description]
    """
    @classmethod
    def setUp(cls):

        # Set up non-modified objects used by all test methods
        user = User.objects.create(username='tom', password='ok')
        user2 = User.objects.create(username='ali', password='ok')
        Group.objects.create(name='hey')

    def test_add(self):
        """Test for method add_user
        """
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        self.assertEquals(group.user_set.get(username='tom'), user)

    def test_add_counter(self):
        """Checks if size of groupprofile is correct
        """
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        user2 = User.objects.get(username='ali')
        group.groupprofile.add_user(user)
        group.groupprofile.add_user(user2)
        self.assertEqual(group.groupprofile.size, 2)

    def test_remove_counter(self):
        """Checks if size is correct after remove_user
        """
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        self.assertEqual(group.groupprofile.size, 1)
        group.groupprofile.remove_user(user)
        self.assertEqual(group.groupprofile.size, 0)

    def test_remove_counter_zero(self):
        """Checks if group exists after removing last user
        """
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.add_user(user)
        group.groupprofile.remove_user(user)
        self.assertFalse(Group.objects.filter(id=group.id).exists())

    def test_group_owner(self):
        """Checks if group owner is set correctly
        """
        group = Group.objects.get(name='hey')
        user = User.objects.get(username='tom')
        group.groupprofile.group_owner = user
        self.assertEqual(group.groupprofile.group_owner, user)
