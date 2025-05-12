from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from offers_orders_app.models import Offer, OfferDetail
from utils.test_utils import TestHelper


class OfferDetailsRetrieveTests(APITestCase):
    """
    Tests for GET /offerdetails/{id}/ endpoint.
    """

    def setUp(self):
        """Initializes test data."""
        # Erstelle einen Benutzer
        self.user = TestHelper.create_user(
            username="testuser", is_business=True)

        # Erstelle ein Angebot und Angebotsdetails
        self.offer = Offer.objects.create(
            user=self.user, title="Test Offer", description="Test Description")
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo Design", "Visitenkarte"],
            offer_type="basic"
        )
        self.url = reverse(
            'offer-details', kwargs={'pk': self.offer_detail.id})

    def test_get_offer_detail_success(self):
        """Tests successful retrieval of an offer detail."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer_detail.id)
        self.assertEqual(response.data['title'], self.offer_detail.title)
        self.assertEqual(response.data['revisions'],
                         self.offer_detail.revisions)
        self.assertEqual(
            response.data['delivery_time_in_days'], self.offer_detail.delivery_time_in_days)
        self.assertEqual(response.data['price'], self.offer_detail.price)
        self.assertEqual(response.data['features'], self.offer_detail.features)
        self.assertEqual(response.data['offer_type'],
                         self.offer_detail.offer_type)

    def test_get_offer_detail_not_found(self):
        """Tests that a 404 is returned if the offer detail does not exist."""
        url = reverse('offer-details',
                      kwargs={'pk': 999999})  # Nicht existierende ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
