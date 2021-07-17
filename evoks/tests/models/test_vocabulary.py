from django.test import TestCase
from vocabularies.models import Vocabulary
from django.contrib.auth.models import User

class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):

        user = User.objects.create(username='jhon', password='ok',email='jhon@example.com')
        Vocabulary.create_vocabulary(name='genel', creator=user.profile)

    def testPermission(self):
        user = User.objects.get(username='jhon')
        vocabulary = Vocabulary.create_vocabulary(name='genel', creator=user.profile)
        print(user.has_perm('owner', vocabulary))

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)