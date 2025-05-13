from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from offers_orders_app.models import Order
from utils.test_utils import TestHelper
from .test_orders_helpers import OrdersTestHelper


class OrderTests(APITestCase):
    """
    Tests for Order endpoints.
    """

    def setUp(self):
        """Set up test data for orders."""
        # Create users
        self.business_user = TestHelper.create_user(
            username="business_user", is_business=True)
        self.customer_user = TestHelper.create_user(
            username="customer_user", is_business=False)
        self.admin_user = TestHelper.create_user(
            username="admin_user", is_staff=True)

        # Authenticate the customer user
        self.token = TestHelper.create_token(self.customer_user)
        TestHelper.auth_client(self.client, self.token)

        # Create an offer and offer detail
        self.offer, self.offer_detail = OrdersTestHelper.create_offer_and_detail(
            user=self.business_user,
            title="Test Offer",
            detail_title="Logo Design"
        )

        # Create an order
        self.order = OrdersTestHelper.create_order(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=self.offer_detail
        )

    # -------------------- GET Tests --------------------

    def test_get_orders_authenticated(self):
        """Tests that authenticated users can retrieve their orders."""
        url = reverse('order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        for order in response.data:
            OrdersTestHelper.check_order_fields(self, order)
            OrdersTestHelper.check_order_data_types(self, order)

    def test_get_orders_unauthenticated(self):
        """Tests that unauthenticated users cannot retrieve orders."""
        self.client.credentials()  # Remove authentication
        url = reverse('order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------- POST Tests --------------------

    def test_post_order_success(self):
        """Tests successful creation of an order."""
        url = reverse('order-list-create')
        payload = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        OrdersTestHelper.check_order_fields(self, response.data)

    def test_post_order_invalid_data(self):
        """Tests that invalid data returns a 400 Bad Request."""
        # Authentifiziere den Benutzer als Kunde
        TestHelper.auth_client(self.client, self.token)

        url = reverse('order-list-create')
        payload = {}  # Fehlende 'offer_detail_id'
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_order_unauthenticated(self):
        """Tests that unauthenticated users cannot create orders."""
        self.client.credentials()  # Remove authentication
        url = reverse('order-list-create')
        payload = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_order_invalid_user(self):
        """Tests that a non-customer user cannot create orders."""
        token = TestHelper.create_token(self.business_user)
        TestHelper.auth_client(self.client, token)
        url = reverse('order-list-create')
        payload = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_order_invalid_offer_detail(self):
        """Tests that an order cannot be created with an invalid offer detail."""
        TestHelper.auth_client(self.client, self.token)
        url = reverse('order-list-create')
        payload = {"offer_detail_id": 9999}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------- PATCH Tests --------------------

    def test_patch_order_success(self):
        """Tests successful update of an order status by a business user."""
        token = TestHelper.create_token(self.business_user)
        TestHelper.auth_client(self.client, token)
        url = reverse('order-detail', args=[self.order.id])
        payload = {"status": "completed"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, payload['status'])

    def test_patch_order_invalid_status(self):
        """Tests that an invalid status returns a 400 Bad Request."""
        token = TestHelper.create_token(self.business_user)
        TestHelper.auth_client(self.client, token)
        url = reverse('order-detail', args=[self.order.id])
        payload = {"status": "invalid_status"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_unauthenticated(self):
        """Tests that unauthenticated users cannot update an order."""
        self.client.credentials()
        url = reverse('order-detail', args=[self.order.id])
        payload = {"status": "completed"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_invalid_user(self):
        """Tests that a customer cannot update an order."""
        url = reverse('order-detail', args=[self.order.id])
        payload = {"status": "completed"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_not_found(self):
        """Tests that updating a non-existent order returns a 404 Not Found."""
        token = TestHelper.create_token(self.business_user)
        TestHelper.auth_client(self.client, token)
        url = reverse('order-detail', args=[9999])
        payload = {"status": "completed"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------- DELETE Tests --------------------

    def test_delete_order_success(self):
        """Tests successful deletion of an order by an admin user."""
        token = TestHelper.create_token(self.admin_user)
        TestHelper.auth_client(self.client, token)
        url = reverse('order-detail', args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_delete_order_unauthenticated(self):
        """Tests that unauthenticated users cannot delete an order."""
        self.client.credentials()
        url = reverse('order-detail', args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_invalid_user(self):
        """Tests that a non-admin user cannot delete an order."""
        url = reverse('order-detail', args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_not_found(self):
        """Tests that deleting a non-existent order returns a 404 Not Found."""
        token = TestHelper.create_token(self.admin_user)
        TestHelper.auth_client(self.client, token)
        url = reverse('order-detail', args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
