from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ...models import Offer, OfferDetail
from users_auth_app.models import UserProfile


class OfferTestHelper:
    """
    Helper class for reusable assertion methods in offer tests.
    """

    @staticmethod
    def create_user(username='john', password='pass', is_business=False):
        """Creates and returns a user, optionally with a business profile."""
        user = User.objects.create_user(username=username, password=password)
        if is_business:
            UserProfile.objects.create(user=user, type='business')
        return user

    @staticmethod
    def create_token(user):
        """Creates and returns a token for the given user."""
        return Token.objects.create(user=user)

    @staticmethod
    def auth_client(client, token):
        """Sets the auth header for a test client."""
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    @staticmethod
    def create_offer(user, title="Grafikdesign-Paket", description="Originalbeschreibung"):
        """Creates and returns an offer for the given user."""
        return Offer.objects.create(user=user, title=title, description=description)

    @staticmethod
    def create_offer_details(offer):
        """Creates all three OfferDetail variants for an offer."""
        detail1 = OfferDetail.objects.create(
            offer=offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100.0,
            features=["Logo"],
            offer_type="basic"
        )
        detail2 = OfferDetail.objects.create(
            offer=offer,
            title="Standard Design",
            revisions=5,
            delivery_time_in_days=10,
            price=120.0,
            features=["Logo Design", "Visitenkarte", "Briefpapier"],
            offer_type="standard"
        )
        detail3 = OfferDetail.objects.create(
            offer=offer,
            title="Premium Design",
            revisions=10,
            delivery_time_in_days=10,
            price=150.0,
            features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
            offer_type="premium"
        )
        return [detail1, detail2, detail3]

    @staticmethod
    def check_offer_fields(testcase, offers):
        """
        Asserts required fields are present in each offer.
        """
        expected_fields = {
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time", "user_details"
        }
        for offer in offers:
            testcase.assertTrue(expected_fields.issubset(set(offer.keys())))
            OfferTestHelper.check_offer_details(testcase, offer)
            OfferTestHelper.check_user_details(testcase, offer)

    @staticmethod
    def check_offer_details(testcase, offer):
        """
        Asserts required fields in offer details.
        """
        testcase.assertIn("details", offer)
        testcase.assertGreater(len(offer["details"]), 0)
        for detail in offer["details"]:
            testcase.assertIn("id", detail)
            testcase.assertIn("url", detail)

    @staticmethod
    def check_user_details(testcase, offer):
        """
        Asserts required fields in user_details field.
        """
        testcase.assertIn("user_details", offer)
        for key in ["first_name", "last_name", "username"]:
            testcase.assertIn(key, offer["user_details"])

    @staticmethod
    def check_data_types(testcase, offers):
        """
        Asserts correct data types in offers list.
        """
        for offer in offers:
            testcase.assertIsInstance(offer["id"], int)
            testcase.assertIsInstance(offer["user"], int)
            testcase.assertIsInstance(offer["title"], str)
            testcase.assertTrue(
                offer["image"] is None or isinstance(offer["image"], str))
            testcase.assertIsInstance(offer["description"], str)
            testcase.assertIsInstance(offer["created_at"], str)
            testcase.assertIsInstance(offer["updated_at"], str)
            testcase.assertIsInstance(offer["min_price"], (int, float))
            testcase.assertIsInstance(offer["min_delivery_time"], int)
            testcase.assertIsInstance(offer["details"], list)
            testcase.assertIsInstance(offer["user_details"], dict)
            OfferTestHelper.check_detail_data_types(testcase, offer["details"])

    @staticmethod
    def check_detail_data_types(testcase, details):
        """
        Asserts correct data types in offer details.
        """
        for detail in details:
            testcase.assertIsInstance(detail["id"], int)
            testcase.assertIsInstance(detail["url"], str)

    @staticmethod
    def check_single_offer_fields(testcase, offer):
        """
        Asserts expected fields for a single offer.
        """
        expected_fields = {
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time"
        }
        testcase.assertTrue(expected_fields.issubset(set(offer.keys())))
        testcase.assertNotIn("user_details", offer)
        OfferTestHelper.check_offer_details(testcase, offer)

    @staticmethod
    def check_single_offer_data_types(testcase, offer):
        """
        Asserts correct data types for a single offer object.
        """
        testcase.assertIsInstance(offer["id"], int)
        testcase.assertIsInstance(offer["user"], int)
        testcase.assertIsInstance(offer["title"], str)
        testcase.assertTrue(
            offer["image"] is None or isinstance(offer["image"], str))
        testcase.assertIsInstance(offer["description"], str)
        testcase.assertIsInstance(offer["created_at"], str)
        testcase.assertIsInstance(offer["updated_at"], str)
        testcase.assertIsInstance(offer["min_price"], (int, float))
        testcase.assertIsInstance(offer["min_delivery_time"], int)
        testcase.assertIsInstance(offer["details"], list)
        OfferTestHelper.check_detail_data_types(testcase, offer["details"])
