from offers_orders_app.models import Order, OfferDetail
from ..tests_offers.test_offers_helpers import OfferTestHelper


class OrdersTestHelper:
    """
    Helper class for reusable assertion methods in order tests.
    """

    @staticmethod
    def create_order(customer_user, business_user, offer_detail, status='in_progress'):
        """Creates and returns an order."""
        return Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            offer_detail=offer_detail,
            status=status
        )

    @staticmethod
    def create_offer_and_detail(user, title="Test Offer", detail_title="Logo Design"):
        """Creates an offer and a single offer detail."""
        offer = OfferTestHelper.create_offer(user=user, title=title)
        offer_detail = OfferDetail.objects.create(
            offer=offer,
            title=detail_title,
            revisions=3,
            delivery_time_in_days=5,
            price=150.0,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic"
        )
        return offer, offer_detail

    @staticmethod
    def check_order_fields(testcase, order):
        """Asserts required fields are present in an order."""
        expected_fields = {
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at"
        }
        testcase.assertTrue(expected_fields.issubset(set(order.keys())))

    @staticmethod
    def check_order_data_types(testcase, order):
        """Asserts correct data types in an order."""
        testcase.assertIsInstance(order["id"], int)
        testcase.assertIsInstance(order["customer_user"], int)
        testcase.assertIsInstance(order["business_user"], int)
        testcase.assertIsInstance(order["title"], str)
        testcase.assertIsInstance(order["revisions"], int)
        testcase.assertIsInstance(order["delivery_time_in_days"], int)
        testcase.assertIsInstance(order["price"], (int, float))
        testcase.assertIsInstance(order["features"], list)
        testcase.assertIsInstance(order["offer_type"], str)
        testcase.assertIsInstance(order["status"], str)
        testcase.assertIsInstance(order["created_at"], str)
        testcase.assertIsInstance(order["updated_at"], str)
