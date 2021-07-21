from django.test import TestCase
from vocabularies.models import Vocabulary
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

class YourTestClass(TestCase):
    @classmethod
    def set_up_test_data(cls):
        user = User.objects.create(username='jhon', password='ok',email='jhon@example.com')
        user.save()
        Vocabulary.create(name='genel', creator=user.profile)

    def test_permission(self):
        user = User.objects.get(username='jhon')
        vocabulary = Vocabulary.objects.get(name='genel')
        permission = Permission.objects.get(name='Owner')
        print(vocabulary.name)
        print(permission)
        print(user.has_perm('vocabularies.owner', vocabulary))
        print(user.has_perm('vocabularies.owner'))

    def test_false_is_false(self):
        self.assertFalse(False)

    def test_false_is_true(self):
        self.assertTrue(True)

    def test_one_plus_one_equals_two(self):
        self.assertEqual(1 + 1, 2)