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

    def test_token_is_created_on_successful_login(self):
        """
        Tests that a token is created when a user successfully logs in.
        """
        payload = {"username": "exampleUser", "password": "strongPassword"}
        response = self.client.post(self.url, data=payload, format="json")

        token = Token.objects.filter(user=self.user).first()
        self.assertIsNotNone(token)
        self.assertEqual(response.data["token"], token.key)

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

    def test_login_fails_with_invalid_json(self):
        """
        Tests login fails when invalid JSON is provided.
        """
        payload = "{username: 'exampleUser', password: 'strongPassword'}"
        response = self.client.post(
            self.url, data=payload, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
