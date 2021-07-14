from django.test import TestCase

from Comment.models import Comment

class test_comment(TestCase):

    def test_init_(self):
        # Test for constuructor. Cheks if given parameter is set
        obj = Comment('test')
        self.assertEquals(obj.text, 'test')
