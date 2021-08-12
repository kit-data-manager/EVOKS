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
    def setUpTestData(cls):
        cls.user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        cls.vocabulary = Vocabulary.create(name='genell', urispace='genelurispace.com', creator=cls.user.profile)
        cls.vocabulary.add_term(name='test')
        cls.term = cls.vocabulary.term_set.get(name='test')


    @classmethod
    def tearDownClass(cls):
        fuseki_dev.delete_vocabulary(cls.vocabulary)


    def test_create(self):
        term = self.term
        self.assertEqual(term.name, 'test')
        self.assertEqual(term.vocabulary, self.vocabulary)


    #no idea how to test this yet
    #test if file contents match query contents?
    def test_export_term_json(self):
        term = self.term
        file = term.export_term('json')
        print(file)


    def test_export_term_ttl(self):
        term = self.term
        file = term.export_term('N3')


    def test_export_term_rdf(self):
        term = self.term
        file = term.export_term('rdf/xml')
