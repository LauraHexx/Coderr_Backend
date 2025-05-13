
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from utils.permission_utils import IsCustomerUser
from .permissions import IsReviewer


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """
    Handles GET /reviews/ and POST /reviews/
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Dynamically assign permissions based on the HTTP method.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filters reviews based on query parameters like business_user_id, reviewer_id, and ordering.
        """
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        ordering = self.request.query_params.get('ordering')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        if ordering in ['updated_at', 'rating', '-updated_at', '-rating']:
            queryset = queryset.order_by(ordering)
        return queryset

    def perform_create(self, serializer):
        """
        Associates the currently authenticated user as the reviewer when creating a review.
        """
        serializer.save(reviewer=self.request.user)


class ReviewRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles GET /reviews/{id}/, PATCH /reviews/{id}/, DELETE /reviews/{id}/
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Assigns the IsReviewer permission for PATCH and DELETE requests.
        Uses default permissions for other methods.
        """
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsReviewer()]
        return super().get_permissions()
