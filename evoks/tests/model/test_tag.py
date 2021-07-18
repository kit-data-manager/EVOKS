from django.test import TestCase
from Tag.models import Tag


class test_tag(TestCase):
    """
    Test class for Tag.
    """

    def test_init_(self):
        """
        Test method for constructor. Checks if given parameters has been set correctly.
        """
        obj = Tag('test')
        self.assertEquals(obj.name, 'test')
