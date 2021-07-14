from django.test import TestCase

from Tag.models import Tag

class test_tag(TestCase):

    def test_init_(self):
        # Test for constuructor. Cheks if given parameter is set        
        obj = Tag('test')
        self.assertEquals(obj.name, 'test')
