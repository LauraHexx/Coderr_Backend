from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


class LoginTests(APITestCase):
    def setUp(self):
        """
        Creates a test user and sets the login endpoint URL.
        """
        self.user = User.objects.create_user(
            username="exampleUser", email="example@mail.de", password="strongPassword"
        )
        self.url = reverse("login")

    def test_login_successful(self):
        """
        Tests that a user can log in with valid credentials and receives expected data.
        """
        payload = {"username": "exampleUser", "password": "strongPassword"}
        response = self.client.post(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "exampleUser")
        self.assertEqual(response.data["email"], "example@mail.de")
        self.assertEqual(response.data["user_id"], self.user.id)

    def test_login_fails_with_wrong_username(self):
        """
        Tests login fails with incorrect username.
        """
        payload = {"username": "wrongUser", "password": "strongPassword"}
        response = self.client.post(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_login_fails_with_wrong_password(self):
        """
        Tests login fails with incorrect password.
        """
        payload = {"username": "exampleUser", "password": "wrongPassword"}
        response = self.client.post(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_login_fails_with_missing_fields(self):
        """
        Tests login fails if required fields are missing (username, password).
        """
        for field in ["username", "password"]:
            payload = {
                key: "test" for key in ["username", "password"] if key != field
            }
            response = self.client.post(self.url, data=payload, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_login_fails_with_empty_payload(self):
        """
        Tests login fails with completely empty JSON payload.
        """
        response = self.client.post(self.url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)

    def test_login_fails_with_non_json_payload(self):
        """
        Tests login fails with non-JSON format payload.
        """
        response = self.client.post(self.url, data="not a json", content_type="text/plain")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fails_when_user_is_inactive(self):
        """
        Tests that inactive users cannot log in.
        """
        self.user.is_active = False
        self.user.save()

        payload = {"username": "exampleUser", "password": "strongPassword"}
        response = self.client.post(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
