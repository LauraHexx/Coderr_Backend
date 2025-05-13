from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db.models import Avg, Count
from offers_orders_app.models import Offer
from reviews_app.models import Review
from users_auth_app.models import UserProfile


class BaseInfoView(APIView):
    """
    Returns general platform statistics.
    """
    permission_classes = [AllowAny]

    def get_statistics(self):
        """
        Helper method to calculate platform statistics.
        """
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(
            avg_rating=Avg('rating'))['avg_rating']
        average_rating = round(average_rating, 1) if average_rating else 0.0
        business_profile_count = UserProfile.objects.filter(
            type='business').count()
        offer_count = Offer.objects.count()

        return {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

    def get(self, request):
        try:
            data = self.get_statistics()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print("DEBUG: Exception occurred:", str(e))
            return Response(
                {"detail": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
