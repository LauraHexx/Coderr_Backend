from django.db.models import Min
from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from utils.permission_utils import IsBusinessUser, IsOwner
from ..models import Offer, OfferDetail
from .serializers import OfferDetailSerializer, OfferRetrieveSerializer, OfferListSerializer, OfferEditSerializer
from .filters import OfferFilter
from .pagination import OfferPagination


class OfferViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations for offers with custom filtering, ordering and permissions.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OfferFilter
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    pagination_class = OfferPagination

    def get_permissions(self):
        """
        Returns custom permissions based on the action type.
        """
        if self.action == 'create':
            return [IsAuthenticated(), IsBusinessUser()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.action == 'list':
            return OfferListSerializer
        if self.action == 'retrieve':
            return OfferRetrieveSerializer
        return OfferEditSerializer

    def get_queryset(self):
        """
        Annotates offers with `min_price` and sorts them for pagination stability.
        """
        return Offer.objects.annotate(
            min_price=Min('details__price')
        ).order_by('min_price')

    def perform_create(self, serializer):
        """
        Assigns the current user as creator of the offer.
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Updates the `updated_at` field.
        """
        serializer.save(updated_at=timezone.now())


class OfferDetailsRetrieveAPIView(generics.RetrieveAPIView):
    """
    Read-only view for a single offer detail object.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
