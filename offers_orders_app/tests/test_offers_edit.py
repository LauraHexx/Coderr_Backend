from .test_helpers import OfferTestHelper
from users_auth_app.models import User, UserProfile
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class OfferCreateTests(APITestCase):
    """Tests for POST /api/offers/ endpoint with token auth and business-user check via UserProfile."""

    def setUp(self):
        """Create business user, profile, token and set auth header."""
        self.user = User.objects.create_user(
            username='testbiz', email='biz@example.com', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user, type='business')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('offer-list')

    def test_create_offer_successfully(self):
        """Test successful creation of offer with valid payload and business user."""
        payload = self._valid_payload()
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._assert_offer_response_data(response.data, payload)

    def test_create_offer_fails_with_less_than_three_details(self):
        """Test that offer creation fails if less than 3 details are provided."""
        payload = self._valid_payload()
        payload["details"] = payload["details"][:2]  # Nur 2 Details

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_fails_without_token(self):
        """Test that unauthenticated request returns 401."""
        self.client.credentials()  # Token entfernen
        payload = self._valid_payload()

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_fails_for_customer_user(self):
        """Test that customer user gets 403 when trying to create an offer."""
        customer_user = User.objects.create_user(
            username='cust', email='cust@example.com', password='password123')
        UserProfile.objects.create(user=customer_user, type='customer')
        token = Token.objects.create(user=customer_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        payload = self._valid_payload()

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _valid_payload(self):
        """Returns a valid payload with exactly 3 offer details."""
        return {
            "title": "Grafikdesign-Paket",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium"
                }
            ]
        }

    def _assert_offer_response_data(self, data, payload):
        """Checks if the response matches the payload structure and values."""
        self.assertIn("id", data)
        self.assertEqual(data["title"], payload["title"])
        self.assertEqual(data["description"], payload["description"])
        self.assertEqual(data["image"], payload["image"])
        self.assertEqual(len(data["details"]), 3)

        for i, expected_detail in enumerate(payload["details"]):
            returned_detail = data["details"][i]
            self.assertIn("id", returned_detail)
            self.assertEqual(
                returned_detail["title"], expected_detail["title"])
            self.assertEqual(
                returned_detail["revisions"], expected_detail["revisions"])
            self.assertEqual(
                returned_detail["delivery_time_in_days"], expected_detail["delivery_time_in_days"])
            self.assertEqual(
                returned_detail["price"], expected_detail["price"])
            self.assertEqual(
                returned_detail["features"], expected_detail["features"])
            self.assertEqual(
                returned_detail["offer_type"], expected_detail["offer_type"])
