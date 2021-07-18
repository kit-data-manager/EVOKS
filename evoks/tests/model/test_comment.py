from django.test import TestCase
from Comment.models import Comment


class test_comment(TestCase):
    """
    Test class for Comment.
    """

    def test_init_(self):
        """
        Test method for constructor. Checks if given parameters has been set correctly.
        """
        obj = Comment('test')
        self.assertEquals(obj.text, 'test')
