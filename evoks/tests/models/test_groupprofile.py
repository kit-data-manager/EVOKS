from django.test import TestCase

from django.contrib.auth.models import Group
from GroupProfile.models import GroupProfile


class GroupProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Group.objects.create(name='hey')

    def test_foo(self):
        group = Group.objects.get(id=1)
        self.assertFalse(False)

    