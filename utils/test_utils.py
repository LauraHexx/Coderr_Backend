from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users_auth_app.models import UserProfile


class TestHelper:
    """
    Helper class for reusable test methods across all apps.
    """

    @staticmethod
    def create_user(username='john', password='pass', is_business=False, is_staff=False):
        """Creates and returns a user, optionally with a business profile."""
        user = User.objects.create_user(
            username=username, password=password, is_staff=is_staff)
        if is_business:
            UserProfile.objects.create(user=user, type='business')
        else:
            UserProfile.objects.create(user=user, type='customer')
        print(user)
        return user

    @staticmethod
    def create_token(user):
        """Creates and returns a token for the given user."""
        return Token.objects.create(user=user)

    @staticmethod
    def auth_client(client, token):
        """Sets the auth header for a test client."""
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
