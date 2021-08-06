from Profile.models import Profile
from logging import PlaceHolder
from django.test import TestCase
from vocabularies.models import Vocabulary, State, Dataformat
from GroupProfile.models import GroupProfile
from django.contrib.auth.models import User, Group
from Term.models import Term
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm, get_perms

class VocabularyTest(TestCase):
    #TODO how to test after remove
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        cls.vocabulary = Vocabulary.create(name='genel', creator=cls.user.profile)

    def test_create(self):
        vocabulary = self.vocabulary
        user = self.user

        #test attributes set correctly
        self.assertEqual(vocabulary.profiles.get(user=user), user.profile)
        self.assertEqual(vocabulary.state, State.DEV)
        self.assertTrue(user.has_perm('owner', vocabulary))
        self.assertIsInstance(vocabulary, Vocabulary)

    def test_get_name(self):
        vocabulary = self.vocabulary
        self.assertEquals(vocabulary.get_name(), 'genel')

    def test_set_live(self):
        vocabulary = self.vocabulary
        vocabulary.set_live()
        self.assertEqual(vocabulary.state, State.LIVE)
    

    def test_set_dev(self):
        vocabulary = self.vocabulary
        with self.assertRaises(ValueError):
            vocabulary.set_dev()
        vocabulary.set_review()
        vocabulary.set_dev()
        self.assertEqual(vocabulary.state, State.DEV)

    def test_set_review(self):
        vocabulary = self.vocabulary
        vocabulary.set_review()
        self.assertEqual(vocabulary.state, State.REVIEW)

    def test_import_vocabulary(self):
        vocabulary = self.vocabulary
        #vocabulary.import_vocabulary()
        #test

    def test_export_vocabulary(self):
        vocabulary = self.vocabulary
        #vocabulary.export_vocabulary()
        #test

    def test_add_and_remove_term(self):
        vocabulary = self.vocabulary
        vocabulary.add_term(name='koeri')
        self.assertIsInstance(vocabulary.term_set.get(name='koeri'), Term)
        vocabulary.remove_term(name='koeri')
        #how test?
        with self.assertRaises(Term.DoesNotExist):
            vocabulary.term_set.get(name='koeri')
        with self.assertRaises(Term.DoesNotExist):
            Term.objects.get(name='koeri')

    def test_add_and_remove_profile(self):
        vocabulary = self.vocabulary
        user = User.objects.create(username='bob', password='ok',
                            email='bob@example.com')
        vocabulary.add_profile(user.profile, 'spectator')
        self.assertEqual(vocabulary.profiles.get(user=user), user.profile)
        self.assertIsInstance(vocabulary.profiles.get(user=user), Profile)
        self.assertTrue(user.has_perm('spectator', vocabulary))
        #remove
        vocabulary.remove_profile(user.profile)
        with self.assertRaises(Profile.DoesNotExist):
            vocabulary.profiles.get(user=user)
        self.assertFalse(user.has_perm('spectator', vocabulary))

    def test_add_and_remove_group(self):
        vocabulary = self.vocabulary
        group = Group.objects.create(name='Krabbelgruppe')
        user = User.objects.create(username='bob', password='ok',
                            email='bob@example.com')
        group.user_set.add(user)
        vocabulary.add_group(group.groupprofile, 'participant')
        self.assertIsInstance(vocabulary.groups.get(group=group), GroupProfile)
        self.assertEqual(vocabulary.groups.get(group=group), group.groupprofile)
        self.assertTrue(user.has_perm('participant', vocabulary))
        #remove
        vocabulary.remove_group(group.groupprofile)
        with self.assertRaises(GroupProfile.DoesNotExist):
            vocabulary.groups.get(group=group)
        self.assertFalse(user.has_perm('participant', vocabulary))

    def test_edit_field(self):
        PlaceHolder

    def test_delete_field(self):
        PlaceHolder

    def test_create_field(self):
        PlaceHolder

    def test_search(self):
        PlaceHolder