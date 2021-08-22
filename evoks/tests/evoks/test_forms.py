from django.test import TestCase
from django.test import Client
from unittest import skip
from evoks.forms import SetPasswordForm
from django.contrib.auth.models import User
from django import forms


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
        self.user.save()

    def test_SetPasswordForm(self) -> None:
        """Tests the SetPasswordForm"""
        form = SetPasswordForm(
            self.user, {'new_password1': 'ok1', 'new_password2': 'ok1'})

        self.assertTrue(form.is_valid())

    def test_SetPasswordForm_mismatch(self) -> None:
        """Tests the SetPasswordForm"""
        form = SetPasswordForm(
            self.user, {'new_password1': 'ok1', 'new_password2': 'ok2'})
        self.assertFalse(form.is_valid())

    def test_SetPasswordForm_save(self) -> None:
        """Tests the SetPasswordForm"""
        form = SetPasswordForm(
            self.user, {'new_password1': 'ok1', 'new_password2': 'ok1'})
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password('ok1'))

    def test_SetPasswordForm_save_commit(self) -> None:
        """Tests the SetPasswordForm"""
        form = SetPasswordForm(
            self.user, {'new_password1': 'ok1', 'new_password2': 'ok1'})
        self.assertTrue(form.is_valid())
        form.save(commit=True)
        user = User.objects.get(email='jhon@example.com')
        self.assertTrue(user.check_password('ok1'))
