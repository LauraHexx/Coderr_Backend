from reviews_app.models import Review


class ReviewTestHelper:
    """
    Helper class for reusable methods in review tests.
    """

    @staticmethod
    def create_review(business_user, reviewer, rating=4, description="Default description"):
        """Creates and returns a review."""
        return Review.objects.create(
            business_user=business_user,
            reviewer=reviewer,
            rating=rating,
            description=description
        )

    @staticmethod
    def get_valid_payload(business_user, rating=5, description="Top Qualität und schnelle Lieferung!"):
        """Returns a valid payload for creating a review."""
        return {
            "business_user": business_user.id,
            "rating": rating,
            "description": description
        }
