from django.test import TestCase
from vocabularies.models import Vocabulary
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

class VocabularyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
        Vocabulary.create(name='genel', creator=user.profile)

    def test_verified_false(self):
        user = User.objects.get(username='jhon')
        self.assertFalse(user.profile.verified)

    def test_permission_after_creation(self):
        user = User.objects.get(username='jhon')
        vocabulary = Vocabulary.objects.get(name='genel')
        print(user.has_perm('owner', vocabulary))

    def test_false_is_false(self):
        self.assertFalse(False)

    def test_false_is_true(self):
        self.assertTrue(True)

    def test_one_plus_one_equals_two(self):
        self.assertEqual(1 + 1, 2)