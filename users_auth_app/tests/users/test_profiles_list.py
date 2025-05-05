# tests/users/test_profile_list_views.py

from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from users_auth_app.models import UserProfile

User = get_user_model()


class ProfileListViewTests(APITestCase):
    """
    Test suite for the profile list view. Tests authenticated access to business and 
    customer profiles, unauthenticated access, and invalid profile types.
    """

    def setUp(self):
        """Sets up users and their profiles for business and customer types."""
        self.business_user = self._create_user(
            'max_business', 'max@business.com', 'Max', 'Mustermann', 'business')
        self.customer_user = self._create_user(
            'customer_jane', 'jane@customer.com', 'Jane', 'Doe', 'customer')

    def _create_user(self, username, email, first_name, last_name, user_type):
        """Creates a user and profile with a specified type and returns the user."""
        user = User.objects.create_user(
            username=username, password='testpass', email=email, first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, type=user_type, tel='987654321',
                                   description=f'{user_type.capitalize()} description')
        token = Token.objects.create(user=user)
        return user, token

    def test_business_profiles_authenticated(self):
        """Tests that business profiles are returned correctly when authenticated."""
        self._test_authenticated_profiles('business', self.business_user)

    def test_customer_profiles_authenticated(self):
        """Tests that customer profiles are returned correctly when authenticated."""
        self._test_authenticated_profiles('customer', self.customer_user)

    def _test_authenticated_profiles(self, profile_type, user):
        """Helper function to test authenticated profile access."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + Token.objects.get(user=user).key)
        url = reverse('profiles-list', kwargs={'type': profile_type})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self._assert_profile_fields(response, profile_type)

    def _assert_profile_fields(self, response, profile_type):
        """Asserts the presence of expected fields in the response data based on profile type."""
        expected_fields = self._get_expected_fields(profile_type)
        self.assertEqual(set(response.data[0].keys()), expected_fields)

    def _get_expected_fields(self, profile_type):
        """Returns the expected fields for a given profile type."""
        if profile_type == 'business':
            return {
                'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type'
            }
        elif profile_type == 'customer':
            return {
                'user', 'username', 'first_name', 'last_name', 'file', 'tel', 'description', 'type'
            }
        return set()

    def test_unauthenticated_access_business(self):
        """Tests that unauthenticated access to business profiles returns 401."""
        self._test_unauthenticated_access('business')

    def test_unauthenticated_access_customer(self):
        """Tests that unauthenticated access to customer profiles returns 401."""
        self._test_unauthenticated_access('customer')

    def _test_unauthenticated_access(self, profile_type):
        """Helper function to test unauthenticated access to profile types."""
        url = reverse('profiles-list', kwargs={'type': profile_type})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_type_returns_400(self):
        """Tests that an invalid profile type returns a 400 Bad Request."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + Token.objects.get(user=self.business_user).key)
        url = reverse('profiles-list', kwargs={'type': 'invalid'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid profile type', response.data['detail'])
