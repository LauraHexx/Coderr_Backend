
from django.contrib.auth import get_user_model
from django.db import models

from rest_framework import serializers

from ..models import Offer, OfferDetail


class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer für die User-Daten (first_name, last_name, username)."""
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username']


class OfferDetailSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for offer detail objects."""

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']  # Only id and url for GET requests
        view_name = 'offerdetails-detail'

    def to_representation(self, instance):
        """Customizes the output to show full details when GET is performed."""
        request = self.context.get('request')
        if request and request.method == 'GET':
            return super().to_representation(instance)

        # If it's a POST or PUT request, show full details for the OfferDetail
        return {
            "title": instance.title,
            "revisions": instance.revisions,
            "delivery_time_in_days": instance.delivery_time_in_days,
            "price": instance.price,
            "features": instance.features,
            "offer_type": instance.offer_type
        }

    def create(self, validated_data):
        """Handle the creation of OfferDetails when POSTing."""
        # Customize the creation process if needed
        offer_detail = OfferDetail.objects.create(**validated_data)
        return offer_detail


class OfferSerializer(serializers.ModelSerializer):
    """Serializer für das Offer-Model."""
    user_details = UserDetailsSerializer(source="user")
    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_details']

    def get_min_price(self, obj):
        """Calculates the minimum price of the associated offer details."""
        return obj.details.aggregate(models.Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        """Calculates the minimum delivery time in days of the associated offer details."""
        return obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]


class OfferDetailFullSerializer(serializers.ModelSerializer):
    """Full serializer for retrieving all fields of an offer detail."""

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type"
        ]
