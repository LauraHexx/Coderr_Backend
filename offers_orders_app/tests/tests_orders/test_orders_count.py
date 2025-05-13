
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from utils.test_utils import TestHelper
from offers_orders_app.tests.tests_orders.test_orders_helpers import OrdersTestHelper


class OrderCountTests(APITestCase):
    """
    Test suite for endpoints that return the count of in-progress and completed orders
    for a specific business user, including authentication and error handling.
    """

    def setUp(self):
        """
        Sets up a business user, a customer user, authenticates the client, 
        creates an offer with details, and initializes in-progress and completed orders for testing.
        """
        self.business_user = TestHelper.create_user(
            username="business_user", is_business=True)
        self.customer_user = TestHelper.create_user(
            username="customer_user", is_business=False)

        self.token = TestHelper.create_token(self.customer_user)
        TestHelper.auth_client(self.client, self.token)

        self.offer, self.offer_detail = OrdersTestHelper.create_offer_and_detail(
            user=self.business_user,
            title="Test Offer",
            detail_title="Test Offer Detail"
        )

        self.in_progress_order = OrdersTestHelper.create_order(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=self.offer_detail,
            status="in_progress"
        )
        self.completed_order = OrdersTestHelper.create_order(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=self.offer_detail,
            status="completed"
        )

        self.non_existent_business_user_id = 9999

    # -------------------- Tests für /order-count/{business_user_id}/ --------------------

    def test_order_count_success(self):
        """Tests that the count of in-progress orders is returned successfully."""
        url = reverse('order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_count": 1})

    def test_order_count_unauthenticated(self):
        """Tests that unauthenticated users cannot access the endpoint."""
        self.client.credentials()
        url = reverse('order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_business_user_not_found(self):
        """Tests that a 404 is returned if the business user does not exist."""
        url = reverse('order-count', args=[self.non_existent_business_user_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------- Tests für /completed-order-count/{business_user_id}/ --------------------

    def test_completed_order_count_success(self):
        """Tests that the count of completed orders is returned successfully."""
        url = reverse('completed-order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"completed_order_count": 1})

    def test_completed_order_count_unauthenticated(self):
        """Tests that unauthenticated users cannot access the endpoint."""
        self.client.credentials()
        url = reverse('completed-order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_order_count_business_user_not_found(self):
        """Tests that a 404 is returned if the business user does not exist."""
        url = reverse('completed-order-count',
                      args=[self.non_existent_business_user_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
