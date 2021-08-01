from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User


class CustomBackendTest(TestCase):
    """Tests the login functionality

    Args:
        TestCase: Subclasses django TestCase
    """
    @classmethod
    def setUpTestData(cls) -> None:
        # Set up non-modified objects used by all test methods
        user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        user.set_password('ok')
        user.save()

    def test_unverified_authentication(self) -> None:
        """Tests what happens if an unverified User tries to log in
        """
        c = Client()
        response = c.post(
            '/login/',
            dict(email='jhon@example.com', password='ok')
        )
        assert response.status_code == 401

    def test_non_existent_user_authentication(self) -> None:
        """Tests what happens if a non existent User tries to log in
        """
        c = Client()
        response = c.post(
            '/login/',
            dict(email='jebediah@example.com', password='ok')
        )
        assert response.status_code == 401

    def test_successful_authentication(self) -> None:
        """Successfull login test
        """
        user = User.objects.get(id=1)
        user.profile.verified = True
        user.save()
        c = Client()
        response = c.post(
            '/login/',
            dict(email='jhon@example.com', password='ok')
        )
        assert response.status_code == 302

    @skip('skip because feature is not implemented yet')
    def test_notify_admins(self):
        c = Client()
        response = c.post(
            '/signup/',
            dict(name='jebediah jombes',
                 email='jebediah@example.com', password='ok')
        )
        print(response)
