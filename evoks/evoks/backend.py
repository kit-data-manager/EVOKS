from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from typing import Optional


class CustomBackend(ModelBackend):
    """CustomBackend used for the login of the user via email and password

    Args:
        object: subclasses ModelBackend
    """

    def authenticate(self, request: HttpRequest, username=None, password=None, **kwargs) -> Optional[User]:
        """Checks if a user with the given email and password exists and if he is verified or an admin.

        Args:
            request (HttpRequest): The Request
            username (str, optional): The email of the User. Defaults to None.
            password (str, optional): The password of the user. Defaults to None.

        Returns:
            Optional: If the check is passed it returns the checked user, otherwise it returns None
        """
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user) and (user.is_staff or user.profile.verified):
            return user

        return None
