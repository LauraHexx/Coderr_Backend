from django_filters.rest_framework import FilterSet, NumberFilter

from ..models import Offer


class OfferFilter(FilterSet):
    """
    A filter class for the Offer model, allowing filtering by:
    - `creator_id`: Filters offers by the ID of the user who created them.
    - `min_price`: Filters offers with a minimum price.
    - `max_delivery_time`: Filters offers with a maximum delivery time in days.
    """
    creator_id = NumberFilter(field_name='user__id')
    min_price = NumberFilter(method='filter_min_price')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

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
