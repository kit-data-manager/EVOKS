from Profile.models import Profile
from logging import PlaceHolder
from django.test import TestCase
from vocabularies.models import Vocabulary, State, Dataformat
from GroupProfile.models import GroupProfile
from django.contrib.auth.models import User, Group
from Term.models import Term
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from evoks.fuseki import fuseki_dev


class TermTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.user = User.objects.create(username='jhon', password='ok',
                                       email='someone@example.com')
        cls.vocabulary = Vocabulary.create(
            name='example', urispace='exampleurispace.com/', creator=cls.user.profile)
        cls.vocabulary.add_term(name='test', uri='coole/uri')
        cls.term = cls.vocabulary.term_set.get(name='test')

    @classmethod
    def tearDown(cls):
        fuseki_dev.delete_vocabulary(cls.vocabulary)

    def test_create(self):
        term = self.term
        self.assertEqual(term.name, 'test')
        self.assertEqual(term.vocabulary, self.vocabulary)
