from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from users_auth_app.models import UserProfile


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

    def _create_user(self):
        """Creates and returns a user for testing."""
        return User.objects.create_user(
            username='Max Mustermann',
            email='max@mustermann@example.com',
            password='testpassword123',
            first_name='Max',
            last_name='Mustermann',
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
            'user': self.user.id + 999,
            'username': 'illegal_change',
            'type': 'illegal_type_change',
            'created_at': '1999-01-01T00:00:00Z',
        }

    def get_auth_token(self):
        """Returns the user's authentication token."""
        return self.token.key

    def _authenticate(self):
        """Authenticates the client with the user's token."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_auth_token())

    def test_get_profile_detail_success(self):
        """Tests authenticated retrieval of profile details."""
        self._authenticate()
        response = self.client.get(self.url)
        self._assert_profile_details(response)

    def test_get_profile_detail_not_authenticated(self):
        """Tests unauthenticated access to profile details returns 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_detail_other_user_forbidden(self):
        """Tests that another authenticated user cannot patch someone else's profile."""
        other_user = User.objects.create_user(
            username='Other User',
            email='other@example.com',
            password='otherpassword'
        )
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token.key)
        response = self.client.patch(self.url, {'location': 'Illegal update'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_profile_detail_not_found(self):
        """Tests that 404 is returned for non-existent profile."""
        self._authenticate()
        url = reverse('profile-detail', kwargs={'pk': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_detail_success(self):
        """Tests updating profile with valid changes while ignoring read-only fields."""
        self._authenticate()
        updated_data = self._get_updated_data()
        response = self.client.patch(self.url, updated_data)
        self._assert_patch_success(response, updated_data)

    def test_patch_profile_detail_not_authenticated(self):
        """Tests patching profile without authentication returns 401."""
        response = self.client.patch(self.url, {'location': 'New Location'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _assert_patch_success(self, response, updated_data):
        """Asserts the patch response is successful and fields were updated."""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_profile_details(
            response, self._expected_patch_result(updated_data))

    def _expected_patch_result(self, updated_data):
        """Builds expected result after patch operation."""
        return {
            'user': self.user.id,
            'username': self.user.username,
            'first_name': updated_data['first_name'],
            'last_name': updated_data['last_name'],
            'email': updated_data['email'],
            'location': updated_data['location'],
            'tel': updated_data['tel'],
            'description': updated_data['description'],
            'working_hours': updated_data['working_hours'],
            'type': self.user_profile.type,
            'created_at': self.user_profile.created_at.isoformat().replace('+00:00', 'Z')
        }

    def _assert_profile_details(self, response, expected_data=None):
        """Verifies response contains correct profile data."""
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()
        expected = expected_data or self._current_profile_data()

        for key, value in expected.items():
            self.assertEqual(response.data[key], value)

    def _current_profile_data(self):
        """Builds profile data dictionary based on current DB state."""
        return {
            'user': self.user.id,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'location': self.user_profile.location,
            'tel': self.user_profile.tel,
            'description': self.user_profile.description,
            'working_hours': self.user_profile.working_hours,
            'type': self.user_profile.type,
            'created_at': self.user_profile.created_at.isoformat().replace('+00:00', 'Z')
        }
