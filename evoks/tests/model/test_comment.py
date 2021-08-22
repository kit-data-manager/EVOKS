from django.test import TestCase
from Comment.models import Comment
from Term.models import Term
from django.contrib.auth.models import User
from vocabularies.models import Vocabulary
from evoks.fuseki import fuseki_dev


class CommentTest(TestCase):
    """
    Test class for Comment.
    """

    @classmethod
    def setUp(cls):
        cls.user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        cls.vocabulary = Vocabulary.create(name='kelime', urispace='', creator=cls.user.profile)
        cls.term = Term.create(name='term', uri='cool/123')
        cls.comment = Comment.create(text='yorum', author=cls.user.profile, vocabulary=cls.vocabulary, term=cls.term)

    @classmethod
    def tearDown(cls):
        fuseki_dev.delete_vocabulary(cls.vocabulary)

    def test_create(self):
        """
        Test method for constructor. Checks if given parameters has been set correctly.
        """
        comment = self.comment
        vocabulary = self.vocabulary
        term = self.term
        self.assertEquals(comment.text, 'yorum')
        self.assertEquals(vocabulary, comment.vocabulary)
        self.assertEquals(term, comment.term)