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

    def get(self, request):
        try:
            # Anzahl der Bewertungen
            review_count = Review.objects.count()

            # Durchschnittliche Bewertung (auf eine Dezimalstelle gerundet)
            average_rating = Review.objects.aggregate(
                avg_rating=Avg('rating'))['avg_rating']

            average_rating = round(
                average_rating, 1) if average_rating else 0.0

            # Anzahl der Geschäftsnutzer
            business_profile_count = UserProfile.objects.filter(
                type='business').count()

            # Anzahl der Angebote
            offer_count = Offer.objects.count()

            # Antwortdaten
            data = {
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            print("DEBUG: Exception occurred:", str(e))  # Debugging-Ausgabe
            return Response(
                {"detail": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
