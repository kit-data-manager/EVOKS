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
    def setUpTestData(cls):
        cls.user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        cls.vocabulary = Vocabulary.create(name='kelime', urispace='', creator=cls.user.profile)
        cls.term = Term.create(name='term')
        cls.tag = Tag.create(name='yorum', author=cls.user.profile, vocabulary=cls.vocabulary, term=cls.term)

    @classmethod
    def tearDown(cls):
        fuseki_dev.delete_vocabulary(cls.vocabulary)


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
