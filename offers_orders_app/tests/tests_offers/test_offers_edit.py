from users_auth_app.models import User, UserProfile
from .test_offers_helpers import OfferTestHelper
from utils.test_utils import TestHelper
from ...models import Offer
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()


class OfferCreateTests(APITestCase):
    """Tests for POST /api/offers/ endpoint with token auth and business-user check via UserProfile."""

    def setUp(self):
        """
        Sets up a business user, generates a token, and authenticates the client for testing.
        """
        self.user = TestHelper.create_user(
            username='test', is_business=True)
        self.token = TestHelper.create_token(self.user)
        TestHelper.auth_client(self.client, self.token)
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
        payload["details"] = payload["details"][:2]

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_fails_without_token(self):
        """Test that unauthenticated request returns 401."""
        self.client.credentials()
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


class OfferPatchTests(APITestCase):
    """
    Test suite for PATCH /offers/<id>/ endpoint with authentication,
    permissions, field structure and error handling.
    """

    def setUp(self):
        """
        Sets up users, authenticates the client, creates an offer, and assigns offer details for testing.
        """
        self.user = TestHelper.create_user()
        self.other_user = TestHelper.create_user(username='hacker')
        self.token = TestHelper.create_token(self.user)
        TestHelper.auth_client(self.client, self.token)
        self.offer = OfferTestHelper.create_offer(self.user)
        offer_details = OfferTestHelper.create_offer_details(self.offer)
        self.detail_basic = offer_details[0]  # First detail in the list
        self.url = reverse('offer-detail', kwargs={'pk': self.offer.pk})

    def test_successful_patch(self):
        """
        Tests successful update of an offer with valid data and token.
        """
        payload = {
            "title": "Updated Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic"
                }
            ]
        }

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_type_cannot_be_changed(self):
        """
        Ensures that changing 'offer_type' in an existing detail returns 400.
        """
        payload = {
            "details": [
                {
                    "id": self.detail_basic.id,
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "standard"
                }
            ]
        }

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("offer_type", str(response.data).lower())

    def test_detail_id_immutability(self):
        """
        Ensures that invalid or spoofed OfferDetail IDs are rejected.
        """
        manipulated_id = 99999

        payload = {
            "details": [
                {
                    "id": manipulated_id,
                    "title": "Illegal Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": 50,
                    "features": ["Fake Feature"],
                    "offer_type": "basic"
                }
            ]
        }

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_with_invalid_data_returns_400(self):
        """
        Sends incomplete/invalid data and expects HTTP 400.
        """
        payload = {
            "details": [
                {
                    "id": self.detail_basic.id,
                    "title": "",  # Invalid: required field
                    "revisions": -1,  # Invalid: negative
                    "delivery_time_in_days": None,  # Invalid: required
                    "price": "free",  # Invalid type
                    "features": "Logo",  # Invalid type: must be list
                    "offer_type": "unknown"  # Invalid choice
                }
            ]
        }

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_patch_missing_offer_type_returns_400(self):
        """
        Ensures that omitting 'offer_type' in a detail returns 400 and a helpful error message.
        """
        payload = {
            "details": [
                {
                    "id": self.detail_basic.id,
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"]
                    # 'offer_type' fehlt absichtlich!
                }
            ]
        }
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Each detail must include 'offer_type'.",
                      str(response.data))

    def test_patch_unauthenticated_returns_401(self):
        """
        Ensures unauthenticated users get 401 response.
        """
        self.client.credentials()
        payload = {"title": "Test"}
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_not_owner_returns_403(self):
        """
        Ensures another authenticated user cannot modify this offer.
        """
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token.key)

        payload = {"title": "Hacked!"}
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_nonexistent_offer_returns_404(self):
        """
        Ensures PATCH on invalid offer ID returns 404.
        """
        invalid_url = reverse('offer-detail', kwargs={'pk': 99999})
        payload = {"title": "Nonexistent"}
        response = self.client.patch(invalid_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDeleteTests(APITestCase):
    """
    Test suite for DELETE /offers/<id>/ endpoint with authentication,
    ownership permissions and error handling.
    """

    def setUp(self):
        """
        Sets up users, authenticates the client, and creates an offer for testing.
        """
        self.user = TestHelper.create_user()
        self.other_user = TestHelper.create_user(username='hacker')
        self.token = TestHelper.create_token(self.user)
        TestHelper.auth_client(self.client, self.token)

        self.offer = OfferTestHelper.create_offer(self.user)
        self.url = reverse('offer-detail', kwargs={'pk': self.offer.pk})

    def test_delete_offer(self):
        """
        Tests that the owner can successfully delete their offer.
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_unauthenticated_returns_401(self):
        """
        Ensures unauthenticated users cannot delete an offer.
        """
        self.client.credentials()  # Clear token
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer_not_owner_returns_403(self):
        """
        Ensures users cannot delete offers they don't own.
        """
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token.key)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_offer_returns_404(self):
        """
        Ensures deleting a nonexistent offer returns 404.
        """
        invalid_url = reverse('offer-detail', kwargs={'pk': 99999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
