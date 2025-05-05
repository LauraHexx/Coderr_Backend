from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailsRetrieveAPIView

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', OfferDetailsRetrieveAPIView.as_view(),
         name='offerdetails-details'),
]
