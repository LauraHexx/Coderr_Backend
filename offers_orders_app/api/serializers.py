
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from rest_framework import serializers
from rest_framework import viewsets

from ..models import Offer, OfferDetail


class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer für die User-Daten (first_name, last_name, username)."""
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username']


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for offer detail objects."""

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        url = reverse('offer-details', kwargs={'pk': obj.pk})
        return url.replace('/api', '', 1)


#################### DIE OBEN LASSEN###############


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer für das Offer-Model."""
    user_details = UserDetailsSerializer(source="user", read_only=True)
    details = OfferDetailHyperlinkedSerializer(
        many=True, read_only=True)

    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']

    def get_min_price(self, obj):
        """Calculates the minimum price of the associated offer details."""
        return obj.details.aggregate(models.Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        """Calculates the minimum delivery time in days of the associated offer details."""
        return obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]


class OfferRetrieveSerializer(OfferListSerializer, serializers.ModelSerializer):
    """Serializer für das Offer-Model."""
    user_details = None

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time']


class OfferEditSerializer(serializers.ModelSerializer):
    """Serializer für das Offer-Model."""
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """
        Validates that all required offer types ('basic', 'standard', 'premium') are included.
        """
        required_types = dict(OfferDetail.OFFER_TYPE_CHOICES).keys()
        offer_types = [detail.get("offer_type") for detail in value]

        missing_types = set(required_types) - set(offer_types)
        if missing_types:
            raise serializers.ValidationError(
                f"At least. Missing offer types ({len(missing_types)}): {', '.join(missing_types)}"
            )
        return value

    def create(self, validated_data):
        """Creates an offer and its associated details."""
        details = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer
