from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """
    Represents a review given by a reviewer to a business user.
    Includes rating, description, and timestamps for creation and updates.
    """
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_reviews"
    )
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username}"
