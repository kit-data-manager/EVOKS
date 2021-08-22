from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User


class EvoksViewsTest(TestCase):
    """Tests the login functionality

    Args:
        TestCase: Subclasses django TestCase
    """
    @classmethod
    def setUp(self) -> None:
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        self.user.profile.verified = True
        self.user.set_password('ok')
        self.user.save()

        self.user = User.objects.create(
            username='unverified@example.com', email='unverified@example.com')
        self.user.set_password('ok')
        self.user.save()

    def test_unverified_authentication(self) -> None:
        """Tests what happens if an unverified User tries to log in
        """
        c = Client()
        response = c.post(
            '/login',
            dict(email='unverified@example.com', password='ok')
        )
        self.assertEqual(response.status_code, 401)

    def test_non_existent_user_authentication(self) -> None:
        """Tests what happens if a non existent User tries to log in
        """
        c = Client()
        response = c.post(
            '/login',
            dict(email='jebediah@example.com', password='ok')
        )
        self.assertEqual(response.status_code, 401)

    def test_successful_authentication(self) -> None:
        """Successfull login test
        """
        c = Client()
        response = c.post(
            '/login',
            dict(email='jhon@example.com', password='ok')
        )
        self.assertEqual(response.status_code, 302)

    def test_get_login(self) -> None:
        """Successfull login test
        """
        c = Client()
        response = c.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_logout(self) -> None:
        """Successfull logout test
        """
        c = Client()
        response = c.post(
            '/login',
            dict(email='jhon@example.com', password='ok')
        )
        self.assertEqual(response.status_code, 302)

        response = c.post('/logout')
        self.assertEqual(response.status_code, 302)

        response = c.get('/vocabularies')
        self.assertEqual(response.status_code, 302)

    def test_signup(self) -> None:
        """Successfull signup test
        """
        c = Client()
        response = c.post(
            '/signup',
            dict(tos='', email='new@example.com',
                 name='new@example.com', password='ok')
        )
        user = User.objects.get(email='new@example.com')
        self.assertIsNotNone(user)
        self.assertFalse(user.profile.verified)
        self.assertEqual(response.status_code, 200)

    def test_signup_no_tos(self) -> None:
        """No ToS 
        """
        c = Client()
        response = c.post(
            '/signup',
            dict(email='new@example.com',
                 name='new@example.com', password='ok')
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_conflict(self) -> None:
        """duplicate mail
        """
        c = Client()
        response = c.post(
            '/signup',
            dict(tos='', email='jhon@example.com',
                 name='jhon@example.com', password='ok')
        )
        self.assertEqual(response.status_code, 400)

    def test_get_signup(self) -> None:
        """Successfull signup test
        """
        c = Client()
        response = c.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')