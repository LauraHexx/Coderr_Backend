from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from reviews_app.tests.test_reviews_helpers import ReviewTestHelper
from utils.test_utils import TestHelper
from offers_orders_app.tests.tests_offers.test_offers_helpers import OfferTestHelper
from offers_orders_app.tests.tests_orders.test_orders_helpers import OrdersTestHelper
from reviews_app.models import Review
from offers_orders_app.models import Order


class BaseInfoViewTests(APITestCase):

    def setUp(self):
        """
        Sets up test data including business users, a reviewer, offers, offer details, reviews, and orders 
        to simulate platform statistics for the BaseInfoView tests.
        """
        self.business_user1 = TestHelper.create_user(
            username="business1", is_business=True)
        self.business_user2 = TestHelper.create_user(
            username="business2", is_business=True)

        self.reviewer = TestHelper.create_user(
            username="reviewer", is_business=False)

        self.offer1 = OfferTestHelper.create_offer(
            user=self.business_user1, title="Offer 1")
        self.offer2 = OfferTestHelper.create_offer(
            user=self.business_user2, title="Offer 2")

        self.offer_details1 = OfferTestHelper.create_offer_details(self.offer1)
        self.offer_details2 = OfferTestHelper.create_offer_details(self.offer2)

        self.offer_detail1 = self.offer_details1[0]
        self.offer_detail2 = self.offer_details2[0]

        ReviewTestHelper.create_review(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=3,
            description="Great service!"
        )
        ReviewTestHelper.create_review(
            business_user=self.business_user2,
            reviewer=self.reviewer,
            rating=5,
            description="Excellent!"
        )

        self.order1 = OrdersTestHelper.create_order(
            customer_user=self.reviewer,
            business_user=self.business_user1,
            offer_detail=self.offer_detail1,
            status="in_progress"
        )
        self.order2 = OrdersTestHelper.create_order(
            customer_user=self.reviewer,
            business_user=self.business_user2,
            offer_detail=self.offer_detail2,
            status="completed"
        )

    def test_base_info_success(self):
        """Tests that the base info endpoint returns correct statistics."""
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 2)
        self.assertAlmostEqual(response.data["average_rating"], 4.0, places=1)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 2)

    def test_base_info_no_reviews(self):
        """Tests the endpoint when there are no reviews."""
        Review.objects.all().delete()
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 2)

    def test_base_info_no_offers(self):
        """Tests the endpoint when there are no offers."""
        self.offer1.delete()
        self.offer2.delete()
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 2)
        self.assertAlmostEqual(response.data["average_rating"], 4.0, places=1)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 0)

    def test_base_info_no_business_users(self):
        """Tests the endpoint when there are no business users."""
        self.business_user1.delete()
        self.business_user2.delete()
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["business_profile_count"], 0)
        self.assertEqual(response.data["offer_count"], 0)

    def test_base_info_no_reviewer(self):
        """Tests the endpoint when the reviewer is deleted."""
        self.reviewer.delete()
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 2)
