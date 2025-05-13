from .test_offers_helpers import OfferTestHelper
from users_auth_app.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from offers_orders_app.models import Offer, OfferDetail
from django.contrib.auth import get_user_model

User = get_user_model()


class OfferGetViewTests(APITestCase):
    """
    Tests for GET /offers/ + /offers/pk endpoint with filters, pagination and structure checks.
    """

    def setUp(self):
        """
        Sets up test data and endpoint URL.
        """
        self.url = reverse('offer-list')
        self.user = User.objects.create_user(username='john', password='pass')
        self.offer = Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professionelles Website-Design...",
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Package",
            revisions=3,
            delivery_time_in_days=7,
            price=100.0,
            features={"feature1": "value1"},
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Premium Package",
            revisions=5,
            delivery_time_in_days=14,
            price=200.0,
            features={"feature1": "value2"},
            offer_type="premium"
        )

    def test_unauthenticated_user_can_access(self):
        """
        Tests that the endpoint allows unauthenticated access.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_status_code_and_structure(self):
        """
        Tests that the API returns status 200 and paginated structure.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_filter_by_creator_id(self):
        """
        Tests filtering offers by creator_id query parameter.
        """
        response = self.client.get(self.url, {'creator_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_filter_by_min_price(self):
        """
        Tests filtering offers by min_price query parameter.
        """
        response = self.client.get(self.url, {'min_price': 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_max_delivery_time(self):
        """
        Tests filtering offers by max_delivery_time query parameter.
        """
        response = self.client.get(self.url, {'max_delivery_time': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination_with_page_parameter(self):
        """
        Tests pagination by requesting page 1.
        """
        response = self.client.get(self.url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_contains_expected_fields(self):
        """
        Tests that each offer contains the expected response fields.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertTrue(len(response.data["results"]) > 0)
        OfferTestHelper.check_offer_fields(self, response.data["results"])

    def test_response_data_types(self):
        """
        Tests that certain fields have the correct data types.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        OfferTestHelper.check_data_types(self, response.data["results"])

    def test_get_single_offer_by_id(self):
        """
        Tests retrieving a single offer by ID.
        """
        detail_url = reverse('offer-detail', kwargs={'pk': self.offer.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        OfferTestHelper.check_single_offer_fields(self, response.data)

    def test_single_offer_data_types(self):
        """
        Tests the data types of a single offer.
        """
        detail_url = reverse('offer-detail', kwargs={'pk': self.offer.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(detail_url)
        OfferTestHelper.check_single_offer_data_types(self, response.data)

    def test_get_single_offer_unauthenticated(self):
        """
        Tests that retrieving a single offer without authentication returns 401.
        """
        detail_url = reverse('offer-detail', kwargs={'pk': self.offer.pk})
        self.client.credentials()  # Remove authentication credentials
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
