
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

    id = serializers.IntegerField()

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
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """
        Validates that if 'details' is provided, it must contain at least one valid entry.
        """
        if value is not None and len(value) == 0:
            raise serializers.ValidationError(
                "If 'details' is provided, it must not be empty."
            )

        valid_types = dict(OfferDetail.OFFER_TYPE_CHOICES).keys()
        offer_types = [detail.get("offer_type") for detail in value or []]

        invalid_types = set(offer_types) - set(valid_types)
        if invalid_types:
            raise serializers.ValidationError(
                f"Invalid offer types: {', '.join(invalid_types)}"
            )

        return value

    def create(self, validated_data):
        """Creates an offer and its associated details."""
        details = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def update(self, instance, validated_data):
        """
        Updates an offer and its existing offer details.
        New details are not allowed. Only existing ones with an ID will be updated.
        """
        details_data = validated_data.pop('details', None)

        # Update Offer-Felder
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {
                detail.id: detail for detail in instance.details.all()}

            for detail_data in details_data:
                print(detail_data)
                detail_id = detail_data.get('id')
                if not detail_id:
                    raise serializers.ValidationError(
                        "Each detail must include its 'id' for updates.")

                if detail_id not in existing_details:
                    raise serializers.ValidationError(
                        f"Detail with id {detail_id} not found for this offer.")

                detail_instance = existing_details[detail_id]
                for attr, value in detail_data.items():
                    if attr in ("offer_type", "id"):
                        continue  # offer_type darf nicht verändert werden
                    setattr(detail_instance, attr, value)
                detail_instance.save()

        return instance
