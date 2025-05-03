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
    def setUp(self):
        self.url = reverse('registration')

    def test_successful_registration(self):
        payload = {
            "username": "Laura Beispiel",
            "email": "laura@example.com",
            "password": "SuperSecurePassword",
            "repeated_password": "SuperSecurePassword",
            "type": "customer"
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("user_id", response.data)

        user = User.objects.get(username="Laura Beispiel")
        self.assertEqual(user.email, "laura@example.com")
        self.assertTrue(Token.objects.filter(user=user).exists())
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        profile = UserProfile.objects.get(user=user)
        self.assertIn(profile.type, ["customer", "business"])


    def test_registration_fails_when_required_fields_missing(self):
        for field in ['username', 'email', 'password', 'repeated_password', 'type']:
            payload = {key: "test" for key in ['username', 'email', 'password', 'repeated_password', 'type'] if key != field}
            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_registration_fails_when_passwords_do_not_match(self):
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
        self.assertFalse(User.objects.filter(email="anna@example.com").exists())

    def test_registration_fails_with_invalid_type(self):
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
        self.assertFalse(User.objects.filter(email="paul@example.com").exists())



    def test_registration_fails_when_email_is_invalid(self):
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
        self.assertFalse(User.objects.filter(username="Invalid Email").exists())
