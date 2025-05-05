from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Custom pagination class that allows dynamic page size via query parameter."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 10000
