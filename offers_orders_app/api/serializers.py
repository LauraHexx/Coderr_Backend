
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from rest_framework import serializers

from ..models import Offer, OfferDetail, Order


############### OFFERS###############

class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializes basic user details such as first name, last name, and username.
    """
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username']


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializes offer details including title, revisions, delivery time, price, features, and offer type.
    """

    id = serializers.IntegerField(required=False)

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes offer details with a hyperlink to the detail view.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        url = reverse('offer-details', kwargs={'pk': obj.pk})
        return url.replace('/api', '', 1)


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializes a list of offers with user details, associated offer details, and calculated minimum price and delivery time.
    """
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
    """
    Serializes a single offer for retrieval, excluding user details.
    """
    user_details = None

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time']


class OfferEditSerializer(serializers.ModelSerializer):
    """
    Serializes offer data for creation or update, including validation for associated offer details.
    """
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
        """
        Updates existing offer details based on the `offer_type`.
        """
        existing_details = self._get_existing_details(instance)
        valid_types = self._get_valid_offer_types()

        for detail_data in details_data:
            self._validate_offer_type(detail_data, valid_types)
            detail_instance = self._get_detail_instance(
                existing_details, detail_data)
            self._validate_detail_immutability(detail_instance, detail_data)
            self._apply_detail_updates(detail_instance, detail_data)

    def _get_existing_details(self, instance):
        """
        Retrieves existing details for the given offer instance.
        """
        return {d.offer_type: d for d in instance.details.all()}

    def _get_valid_offer_types(self):
        """
        Retrieves valid offer types from the model's choices.
        """
        return dict(OfferDetail.OFFER_TYPE_CHOICES).keys()

    def _validate_offer_type(self, detail_data, valid_types):
        """
        Validates that the `offer_type` is present and valid.
        """
        offer_type = detail_data.get('offer_type')
        if not offer_type or offer_type not in valid_types:
            raise serializers.ValidationError(
                f"Invalid or missing 'offer_type': {offer_type}"
            )

    def _get_detail_instance(self, existing_details, detail_data):
        """
        Retrieves the detail instance based on the `offer_type`.
        """
        offer_type = detail_data['offer_type']
        if offer_type not in existing_details:
            raise serializers.ValidationError(
                f"No existing detail found for 'offer_type': {offer_type}"
            )
        return existing_details[offer_type]

    def _validate_detail_immutability(self, detail_instance, detail_data):
        """
        Validates that immutable fields like `id` and `offer_type` are not changed.
        """
        if 'id' in detail_data and detail_data['id'] != detail_instance.id:
            raise serializers.ValidationError(
                f"Changing 'id' is not allowed for detail with offer_type '{detail_instance.offer_type}'."
            )
        if 'offer_type' in detail_data and detail_data['offer_type'] != detail_instance.offer_type:
            raise serializers.ValidationError(
                f"Changing 'offer_type' is not allowed for detail with id {detail_instance.id}."
            )

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
        """
        Applies field updates to an existing detail instance.
        """
        for attr, value in detail_data.items():
            if attr == "id" or attr == "offer_type":
                continue  # Skip immutable fields
            setattr(instance, attr, value)
        instance.save()

############### ORDERS###############


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializes order data with details from the associated offer, including title, revisions, delivery time, and price.
    """
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(
        source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(
        source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.FloatField(source='offer_detail.price', read_only=True)
    features = serializers.JSONField(
        source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(
        source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_user',
                            'business_user', 'created_at', 'updated_at']
