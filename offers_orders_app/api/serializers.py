
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from rest_framework import serializers
from rest_framework import viewsets

from ..models import Offer, OfferDetail


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username']


class OfferDetailSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)

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

    user_details = None

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time']


class OfferEditSerializer(serializers.ModelSerializer):

    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """Validates presence, length, and type of offer details."""
        self._validate_empty_details(value)
        self._validate_minimum_details(value)
        self._validate_offer_types(value)
        return value

    def _validate_empty_details(self, value):
        """Ensures 'details' is not an empty list if provided."""
        if value is not None and len(value) == 0:
            raise serializers.ValidationError(
                "If 'details' is provided, it must not be empty."
            )

    def _validate_minimum_details(self, value):
        """Ensures at least 3 details are present on POST request."""
        if self.context['request'].method == 'POST' and len(value) < 3:
            raise serializers.ValidationError(
                "At least 3 offer details are required."
            )

    def _validate_offer_types(self, value):
        """Ensures all detail offer types are valid."""
        valid_types = dict(OfferDetail.OFFER_TYPE_CHOICES).keys()
        offer_types = [detail.get("offer_type") for detail in value or []]
        invalid_types = set(offer_types) - set(valid_types)
        if invalid_types:
            raise serializers.ValidationError(
                f"Invalid offer types: {', '.join(invalid_types)}"
            )

    def create(self, validated_data):
        """Creates an offer with associated details."""
        details = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        self._create_details(details, offer)
        return offer

    def _create_details(self, details, offer):
        """Creates related offer detail instances."""
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)

    def update(self, instance, validated_data):
        """Updates offer and related details by ID."""
        details_data = validated_data.pop('details', None)
        self._update_offer_fields(instance, validated_data)
        if details_data is not None:
            self._update_offer_details(instance, details_data)
        return instance

    def _update_offer_fields(self, instance, validated_data):
        """Updates basic fields of the offer."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def _update_offer_details(self, instance, details_data):
        """Updates existing offer details only (by ID)."""
        existing = {d.id: d for d in instance.details.all()}
        for detail_data in details_data:
            self._update_single_detail(detail_data, existing)

    def _update_single_detail(self, detail_data, existing_details):
        """Updates a single detail if ID is present and valid."""
        detail_id = detail_data.get('id')
        if not detail_id:
            raise serializers.ValidationError(
                "Each detail must include its 'id' for updates."
            )
        if detail_id not in existing_details:
            raise serializers.ValidationError(
                f"Detail with id {detail_id} not found for this offer."
            )
        detail_instance = existing_details[detail_id]
        self._validate_offer_type_unchanged(detail_instance, detail_data)
        self._apply_detail_updates(detail_instance, detail_data)

    def _validate_offer_type_unchanged(self, instance, detail_data):
        """Prevents changes to 'offer_type' field."""
        if "offer_type" in detail_data:
            new_type = detail_data["offer_type"]
            if new_type != instance.offer_type:
                raise serializers.ValidationError(
                    f"Changing 'offer_type' is not allowed for detail with id {instance.id}."
                )

    def _apply_detail_updates(self, instance, detail_data):
        """Applies field updates to a single detail instance."""
        for attr, value in detail_data.items():
            if attr == "id":
                continue
            setattr(instance, attr, value)
        instance.save()
