from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Offer(models.Model):
    """
    Represents a user-created offer containing multiple detailed packages.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="offers"
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='offer_pictures/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class OfferDetail(models.Model):
    """Model for offer details."""
    offer = models.ForeignKey(
        Offer, related_name="details", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.FloatField()
    features = models.JSONField()
    offer_type = models.CharField(max_length=50, choices=[(
        'basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')])

    def __str__(self):
        return self.title
