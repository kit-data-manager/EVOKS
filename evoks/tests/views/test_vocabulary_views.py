from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User
from vocabularies.models import Vocabulary


class Vocabulary_views_test(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        cls.user.set_password('ok')
        cls.user.save()
        cls.vocabulary = Vocabulary.objects.create(name='genel')
        cls.vocabulary.save()
    
    def test_settings_view(self):
        c = Client()
        response = c.post(
            '/vocabularies/genel/settings'.format(self.vocabulary.name),
        )
        #c.post.__setattr__('vocabulary-setting1')
        self.assertTemplateUsed(response, "vocabulary_setting.html")
        self.assertContains(
            response,
            '<input type="radio" name="vocabulary-setting2" value="Development" {% ifequal vocabulary.state "REVIEW" %} checked {% endifequal %} class="h-4 w-4 mt-0.5 cursor-pointer text-regal-blue border-gray-300 focus:ring-regal-blue" aria-labelledby="privacy-setting-1-label" aria-describedby="privacy-setting-1-description">',
        )