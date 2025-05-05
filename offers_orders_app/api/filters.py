from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from ..models import Offer


class OfferFilter(FilterSet):
    min_price = NumberFilter(method='filter_min_price')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['user']  # Filters by the creator user (creator_id)

    def filter_min_price(self, queryset, name, value):
        """
        Filters offers where the price is greater than or equal to the given value.
        """
        return queryset.filter(details__price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """
        Filters offers where the delivery time is less than or equal to the given value.
        """
        return queryset.filter(details__delivery_time_in_days__lte=value)
