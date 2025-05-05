from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailFullSerializer
from .permissions import IsBusinessUser, IsOfferCreator
from .filters import OfferFilter
from .pagination import OfferPagination


class OfferViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations for offers with custom filtering, ordering and permissions.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OfferFilter
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    pagination_class = OfferPagination

    # def get_permissions(self):
    #    """
    #    Returns custom permissions based on the action type.
    #    """
    #    if self.action == 'create':
    #        return [IsAuthenticated(), IsBusinessUser()]
    #    if self.action in ['update', 'partial_update', 'destroy']:
    #        return [IsAuthenticated(), IsOfferCreator()]
    #    return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        """
        Assigns the current user as creator of the offer.
        """
        serializer.save(user=self.request.user)


class OfferDetailsRetrieveAPIView(generics.RetrieveAPIView):
    """
    Read-only view for a single offer detail object.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailFullSerializer
    permission_classes = [AllowAny]
