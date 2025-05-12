from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from reviews_app.models import Review
from utils.test_utils import TestHelper
from .test_reviews_helpers import ReviewTestHelper


class ReviewListCreateTests(APITestCase):
    """
    Tests for GET /reviews/ and POST /reviews/
    """

    def setUp(self):
        """Set up test data for reviews."""
        self.business_user = TestHelper.create_user(
            username="business_user", is_business=True)
        self.reviewer = TestHelper.create_user(
            username="reviewer", is_business=False)

        self.token = TestHelper.create_token(self.reviewer)
        TestHelper.auth_client(self.client, self.token)

        self.review = ReviewTestHelper.create_review(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description="Very professional service."
        )

        self.list_url = reverse('review-list-create')

    def test_get_reviews_success(self):
        """Tests successful retrieval of reviews."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_reviews_unauthenticated(self):
        """Tests that unauthenticated users cannot retrieve reviews."""
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_reviews_by_business_user(self):
        """Tests filtering reviews by business_user_id."""
        response = self.client.get(
            self.list_url, {'business_user_id': self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['business_user'], self.business_user.id)

    def test_filter_reviews_by_reviewer(self):
        """Tests filtering reviews by reviewer_id."""
        response = self.client.get(
            self.list_url, {'reviewer_id': self.reviewer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reviewer'], self.reviewer.id)

    def test_order_reviews_by_updated_at(self):
        """Tests ordering reviews by updated_at."""
        response = self.client.get(self.list_url, {'ordering': 'updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        updated_at_values = [review['updated_at'] for review in response.data]
        self.assertEqual(updated_at_values, sorted(updated_at_values))

    def test_order_reviews_by_rating(self):
        """Tests ordering reviews by rating."""
        response = self.client.get(self.list_url, {'ordering': 'rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        ratings = [review['rating'] for review in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_post_review_success(self):
        """Tests successful creation of a review."""
        new_business_user = TestHelper.create_user(
            username="new_business_user", is_business=True)
        payload = ReviewTestHelper.get_valid_payload(new_business_user)
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(response.data['rating'], payload['rating'])
        self.assertEqual(response.data['description'], payload['description'])

    def test_post_review_duplicate_error(self):
        """Tests that a reviewer cannot create multiple reviews for the same business user."""
        payload = ReviewTestHelper.get_valid_payload(
            self.business_user, description="Another review.")
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You can only review a business user once.",
                      str(response.data))

    def test_post_review_unauthenticated(self):
        """Tests that unauthenticated users cannot create reviews."""
        self.client.credentials()
        payload = ReviewTestHelper.get_valid_payload(
            self.business_user, description="Unauthenticated review.")
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_review_not_allowed_for_business_user(self):
        """Tests that business users cannot create reviews."""
        business_user = TestHelper.create_user(
            username="business_user2", is_business=True)
        token = TestHelper.create_token(business_user)
        TestHelper.auth_client(self.client, token)
        payload = ReviewTestHelper.get_valid_payload(self.business_user)
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
