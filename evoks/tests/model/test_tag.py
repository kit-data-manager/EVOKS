from django.test import TestCase
from Tag.models import Tag
from Term.models import Term
from django.contrib.auth.models import User
from vocabularies.models import Vocabulary
from evoks.fuseki import fuseki_dev


class TagTest(TestCase):
    """
    Test class for Tag.
    """

    @classmethod
    def setUp(self):
        self.user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        self.vocabulary = Vocabulary.create(name='example', urispace='www.example.com/', creator=self.user.profile)
        self.term = Term.create(name='term', uri='coole/uri')
        self.tag = Tag.create(name='yorum', author=self.user.profile, vocabulary=self.vocabulary, term=self.term)

    @classmethod
    def tearDown(self):
        fuseki_dev.delete_vocabulary(self.vocabulary)


    def test_create(self):
        """
        Test method for constructor. Checks if given parameters has been set correctly.
        """
        tag = self.tag
        vocabulary = self.vocabulary
        term = self.term
        self.assertEquals(tag.name, 'yorum')
        self.assertEquals(vocabulary, tag.vocabulary)
        self.assertEquals(term, tag.term)
