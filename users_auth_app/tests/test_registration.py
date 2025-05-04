from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from users_auth_app.models import UserProfile 

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
from users_auth_app.models import UserProfile 



class RegistrationTests(APITestCase):
    """Test suite for user registration."""

    def setUp(self):
        """Sets up the registration endpoint URL before each test."""
        self.url = reverse('registration')

    def test_successful_registration(self):
        """Tests successful user registration with valid input data."""
        payload = self._valid_payload()
        response = self.client.post(self.url, data=payload, format='json')

        self._assert_success_response(response)
        self._assert_user_created_correctly(payload)

    def _valid_payload(self):
        """Returns a valid payload for user registration."""
        return {
            "username": "Laura Beispiel",
            "email": "laura@example.com",
            "password": "SuperSecurePassword",
            "repeated_password": "SuperSecurePassword",
            "type": "customer"
        }

    def _assert_success_response(self, response):
        """Asserts that the success response contains expected fields."""
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in ["token", "username", "email", "user_id"]:
            self.assertIn(key, response.data)

    def _assert_user_created_correctly(self, payload):
        """Asserts that User, Token, and UserProfile were correctly created."""
        user = User.objects.get(username=payload["username"])
        self.assertEqual(user.email, payload["email"])
        self.assertTrue(Token.objects.filter(user=user).exists())
        profile = UserProfile.objects.get(user=user)
        self.assertIn(profile.type, ["customer", "business"])

    def test_registration_fails_when_required_fields_missing(self):
        """Tests registration failure when required fields are missing."""
        required_fields = ['username', 'email', 'password', 'repeated_password', 'type']
        for field in required_fields:
            payload = {f: "test" for f in required_fields if f != field}
            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_registration_fails_when_passwords_do_not_match(self):
        """Tests registration failure when passwords do not match."""
        payload = {
            "username": "Anna Beispiel",
            "email": "anna@example.com",
            "password": "Password123",
            "repeated_password": "WrongPassword123",
            "type": "customer"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(email=payload["email"]).exists())

    def test_registration_fails_with_invalid_type(self):
        """Tests registration failure when an invalid user type is provided."""
        payload = {
            "username": "Paul Test",
            "email": "paul@example.com",
            "password": "securePassword",
            "repeated_password": "securePassword",
            "type": "invalid_type"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        self.assertFalse(User.objects.filter(email=payload["email"]).exists())

    def test_registration_fails_when_email_is_invalid(self):
        """Tests registration failure when email format is invalid."""
        payload = {
            "username": "Invalid Email",
            "email": "not-an-email",
            "password": "pass123",
            "repeated_password": "pass123",
            "type": "business"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertFalse(User.objects.filter(username=payload["username"]).exists())