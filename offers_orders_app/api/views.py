from django.db import models
from django.db.models import Min
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError, NotFound
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from users_auth_app.models import User, UserProfile

from utils.permission_utils import IsBusinessUser, IsOwner, IsCustomerUser
from ..models import Offer, OfferDetail, Order
from .serializers import OfferDetailSerializer, OfferRetrieveSerializer, OfferListSerializer, OfferEditSerializer, OrderSerializer
from .filters import OfferFilter
from .pagination import OfferPagination

############### OFFERS###############


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
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
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


############### ORDERS###############

class OrderListCreateAPIView(generics.ListCreateAPIView):
    """
    Handles GET /orders/ and POST /orders/
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Dynamically assign permissions based on the HTTP method.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Returns orders where the current user is either the customer or the business user.
        """
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

    def perform_create(self, serializer):
        """
        Creates an order by associating the current user, the business user, and the specified offer detail.
        Validates the presence and existence of the offer detail.
        """
        user = self.request.user
        offer_detail_id = self.request.data.get('offer_detail_id')

        if not offer_detail_id:
            raise ValidationError(
                {"offer_detail_id": "This field is required."})

        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound(
                {"offer_detail_id": "The specified offer detail does not exist."})

        serializer.save(
            customer_user=user,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail
        )


class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles GET /orders/{id}/, PATCH /orders/{id}/, and DELETE /orders/{id}/
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Dynamically assign permissions based on the HTTP method.
        """
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsBusinessUser()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class OrderDeleteAPIView(generics.DestroyAPIView):
    """
    Handles DELETE /orders/{id}/
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


############### ORDER COUNT###############


class OrderCountView(APIView):
    """
    Returns the count of in-progress orders for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Returns the count of in-progress orders for a specific business user.
        Responds with 404 if the business user is not found.
        """
        try:
            if not User.objects.filter(id=business_user_id, userprofile__type='business').exists():
                return Response(
                    {"detail": "Business user not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            order_count = Order.objects.filter(
                business_user_id=business_user_id,
                status='in_progress'
            ).count()

            return Response({"order_count": order_count}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompletedOrderCountView(APIView):
    """
    Returns the count of completed orders for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Returns the count of completed orders for a specific business user.
        Responds with 404 if the business user is not found.
        """
        try:
            if not User.objects.filter(id=business_user_id, userprofile__type='business').exists():
                return Response(
                    {"detail": "Business user not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            completed_order_count = Order.objects.filter(
                business_user_id=business_user_id,
                status='completed'
            ).count()

            return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
