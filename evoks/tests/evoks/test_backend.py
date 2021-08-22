from evoks.backend import CustomBackend
from django.test import TestCase
from django.contrib.auth.models import User

from django.http.request import HttpRequest


class EvoksFormsTest(TestCase):
    """Tests the forms

    Args:
        TestCase: Subclasses django TestCase
    """
    @classmethod
    def setUp(self) -> None:
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        self.user.set_password('ok')
        self.user.profile.verified = True
        self.user.save()

        self.user_not_active = User.objects.create(
            username='inactive@example.com', email='inactive@example.com')
        self.user_not_active.set_password('ok')
        self.user_not_active.profile.verified = True
        self.user_not_active.is_active = False
        self.user_not_active.save()

        self.user_staff = User.objects.create(
            username='staff@example.com', email='staff@example.com')
        self.user_staff.set_password('ok')
        self.user_staff.is_staff = True
        self.user_staff.save()

        self.user_not_verified = User.objects.create(
            username='unverified@example.com', email='unverified@example.com')
        self.user_not_verified.set_password('ok')
        self.user_not_verified.profile.verified = False
        self.user_not_verified.save()
        self.backend = CustomBackend()

    def test_authenticate(self) -> None:
        request = HttpRequest()
        user = self.backend.authenticate(
            request, username=self.user.username, password='ok')
        self.assertEqual(user, self.user)

    def test_authenticate_invalid_user(self) -> None:
        request = HttpRequest()
        user = self.backend.authenticate(
            request, username='doesnotexist', password='ok')
        self.assertIsNone(user)

    def test_authenticate_invalid_password(self) -> None:
        request = HttpRequest()
        user = self.backend.authenticate(
            request, username=self.user.username, password='notok')
        self.assertIsNone(user)

    def test_authenticate_not_verified(self) -> None:
        request = HttpRequest()
        user = self.backend.authenticate(
            request, username=self.user_not_verified.username, password='ok')
        self.assertIsNone(user)

    def test_authenticate_not_active(self) -> None:
        request = HttpRequest()
        user = self.backend.authenticate(
            request, username=self.user_not_active.username, password='ok')
        self.assertIsNone(user)

    def test_authenticate(self) -> None:
        request = HttpRequest()
        user = self.backend.authenticate(
            request, username=self.user_staff.username, password='ok')
        self.assertEqual(user, self.user_staff)
