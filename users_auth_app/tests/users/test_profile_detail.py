from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from users_auth_app.models import UserProfile
import random
import string
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from users_auth_app.models import UserProfile


class ProfileDetailTests(APITestCase):
    """
    Test suite for profile detail endpoints, covering authenticated retrieval,
    profile updates, and access control scenarios.
    """

    def setUp(self):
        """Initializes user, profile, and token before each test."""
        self.user = self._create_user()
        self.user_profile = self._create_user_profile(self.user)
        self.token = Token.objects.create(user=self.user)
        self.url = reverse(
            'profile-detail', kwargs={'pk': self.user_profile.id})

    def _get_profile_object(self):
        """Returns the UserProfile object for the current user."""
        return self.user_profile

    def _create_user(self):
        """Creates and returns a unique user for testing."""
        username = 'user_' + \
            ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="TestPassword123",
            first_name='Max',
            last_name='Mustermann',
        )

    def _create_other_user(self):
        """Creates and returns another unique user for testing."""
        username = 'other_user_' + \
            ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="OtherPassword123"
        )

    def _create_user_profile(self, user):
        """Creates and returns a user profile for testing."""
        return UserProfile.objects.create(
            user=user,
            location="Test Location",
            tel="1234567890",
            description="A test description",
            working_hours="9-5",
            type="business"
        )

    def _get_auth_token(self):
        """Returns the user's authentication token."""
        return self.token.key

    def _authenticate(self):
        """Authenticates the client with the user's token."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self._get_auth_token())

    def _assert_profile_details(self, response, expected_data=None, user=None, profile=None):
        """Asserts the profile response is correct."""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        (user or self.user).refresh_from_db()
        (profile or self.user_profile).refresh_from_db()
        expected = expected_data or self._current_profile_data(user, profile)
        for key, value in expected.items():
            self.assertEqual(response.data[key], value)

    def _current_profile_data(self, user=None, profile=None):
        """Builds profile data dictionary based on current DB state."""
        user = user or self.user
        profile = profile or self.user_profile
        return {
            'user': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'location': profile.location,
            'tel': profile.tel,
            'description': profile.description,
            'working_hours': profile.working_hours,
            'type': profile.type,
            'created_at': profile.created_at.isoformat().replace('+00:00', 'Z')
        }

    def test_get_own_profile(self):
        """Tests authenticated retrieval of the own profile."""
        self._authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_profile_details(response)

    def test_get_other_user_profile(self):
        """Tests authenticated retrieval of another user's profile."""
        other_user = self._create_other_user()
        other_user_profile = self._create_user_profile(other_user)
        other_user_token = Token.objects.create(user=other_user)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + other_user_token.key)
        other_user_url = reverse(
            'profile-detail', kwargs={'pk': other_user_profile.id})
        response = self.client.get(other_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_profile_details(
            response, user=other_user, profile=other_user_profile)

    def test_get_profile_detail_not_authenticated(self):
        """Tests unauthenticated access to profile details returns 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_detail_success(self):
        """Tests updating profile with valid changes while ignoring read-only fields."""
        self._authenticate()
        updated_data = self._get_updated_data()
        response = self.client.patch(self.url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_patch_success(response, updated_data)

    def test_patch_profile_readonly_fields_ignored(self):
        """Ensures read-only fields like 'user' or 'created_at' cannot be overwritten."""
        self._authenticate()
        original_profile = self._get_profile_object()

        patch_data = self._get_patch_data()
        response = self.client.patch(self.url, patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = self._get_profile_object()

        self.assertEqual(profile.user.id, original_profile.user.id)
        self.assertEqual(profile.username, original_profile.username)
        self.assertEqual(profile.created_at, original_profile.created_at)

    def test_patch_profile_detail_not_authenticated(self):
        """Tests patching profile without authentication returns 401."""
        response = self.client.patch(self.url, {'location': 'New Location'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _get_updated_data(self):
        """Returns updated data with both allowed and read-only fields."""
        return {
            'location': 'New Location',
            'tel': '0987654321',
            'description': 'Updated description',
            'working_hours': '10-6',
            'first_name': 'Erika',
            'last_name': 'Musterfrau',
            'email': 'musterfrau@test.de',
        }

    def _assert_patch_success(self, response, updated_data):
        """Asserts the patch response is successful and fields were updated."""
        self._assert_profile_details(response, updated_data)

    def _get_patch_data(self):
        """Returns the patch data with read-only fields that shouldn't be updated."""
        return {
            "user": 1000,
            "username": "Not allowed",
            "type": "notallowed",
            "created_at": "1999-01-01T00:00:00Z",
        }

    def test_get_profile_detail_not_found(self):
        """Tests that 404 is returned for non-existent profile."""
        self._authenticate()
        url = reverse('profile-detail', kwargs={'pk': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_detail_other_user_forbidden(self):
        """Tests that another authenticated user cannot patch someone else's profile."""
        other_user = self._create_other_user()
        Token.objects.create(user=other_user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + other_user.auth_token.key)
        response = self.client.patch(self.url, {'location': 'Illegal update'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
