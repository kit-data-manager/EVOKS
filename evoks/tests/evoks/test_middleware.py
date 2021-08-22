from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser, User, Group
from django.http.request import HttpRequest
from typing import Optional
from django.test import Client
from evoks.middleware import LoginRequiredMiddleware, PartOfVocabularyMiddleware
from django.test import TestCase
from unittest.mock import MagicMock
from unittest import skip
from django.contrib.auth import logout
from evoks.fuseki import fuseki_dev
from vocabularies.models import Vocabulary


class LoginRequiredMiddlewareTest(TestCase):
    @classmethod
    def setUp(self) -> None:
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        self.user.set_password('ok')
        self.user.profile.verified = True
        self.user.save()
        get_response = MagicMock()

        self.middleware = LoginRequiredMiddleware(get_response)

    def test_LoginRequiredMiddleware_no_login(self) -> None:
        request = HttpRequest()
        self.assertRaises(
            AssertionError, self.middleware.process_view, request, None, None, None)

    def test_LoginRequiredMiddleware(self) -> None:
        request = HttpRequest()
        request.user = self.user
        self.assertIsNone(self.middleware.process_view(
            request, None, None, None))

    def test_LoginRequiredMiddleware_user_not_authorized(self) -> None:
        request = HttpRequest()
        request.user = AnonymousUser()
        code = self.middleware.process_view(
            request, None, None, None).status_code
        self.assertEqual(code, 302)

    def test_LoginRequiredMiddleware_user_not_authorized_exempt(self) -> None:
        request = HttpRequest()
        request.path_info = 'logout'
        request.user = AnonymousUser()
        self.assertIsNone(self.middleware.process_view(
            request, None, None, None))

    def test_LoginRequiredMiddleware_user_not_authorized_reset(self) -> None:
        request = HttpRequest()
        request.path = '/reset/abc/123'
        request.path_info = '/reset/abc/123'
        request.user = AnonymousUser()
        self.assertIsNone(self.middleware.process_view(
            request, None, None, None))


class PartOfVocabularyMiddlewareTest(TestCase):
    @classmethod
    def setUp(self) -> None:
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        self.user.set_password('ok')
        self.user.profile.verified = True
        self.user.save()
        get_response = MagicMock()

        self.user_in_group = User.objects.create(
            username='user_in_group@example.com', email='user_in_group@example.com')
        self.user_in_group.set_password('ok')
        self.user_in_group.profile.verified = True
        self.user_in_group.save()

        self.group = Group.objects.create(name='hey')
        self.group.user_set.add(self.user_in_group)

        self.vocabulary = Vocabulary.create(
            name='test_vocabulary_402013', urispace='http://www.testurispace.de/', creator=self.user.profile)
        self.vocabulary.add_group(self.group.groupprofile, 'participant')

        self.user_no_vocabulary = User.objects.create(
            username='user_no_vocabulary@example.com', email='user_no_vocabulary@example.com')
        self.user_no_vocabulary.set_password('ok')
        self.user_no_vocabulary.profile.verified = True
        self.user_no_vocabulary.save()

        self.middleware = PartOfVocabularyMiddleware(get_response)

    @classmethod
    def tearDown(self):
        try:
            fuseki_dev.delete_vocabulary(self.vocabulary)
        except:
            pass

    def test_PartOfVocabularyMiddleware(self) -> None:
        self.assertEqual(True, True)
        request = HttpRequest()
        request.user = self.user
        self.assertIsNone(self.middleware.process_view(
            request, None, None, {'voc_name': self.vocabulary.name}))

    def test_PartOfVocabularyMiddleware_bad_vocabulary(self) -> None:
        request = HttpRequest()
        request.user = self.user
        self.assertEqual(self.middleware.process_view(
            request, None, None, {'voc_name': 'doesntexist'}).status_code, 404)

    def test_PartOfVocabularyMiddleware_no_vocabulary(self) -> None:
        request = HttpRequest()
        request.user = self.user_no_vocabulary
        self.assertEqual(self.middleware.process_view(
            request, None, None, {'voc_name': self.vocabulary.name}).status_code, 302)

    def test_PartOfVocabularyMiddleware_in_group(self) -> None:
        request = HttpRequest()
        request.user = self.user_in_group
        self.assertIsNone(self.middleware.process_view(
            request, None, None, {'voc_name': self.vocabulary.name}))
