
from django.contrib import admin
from django.urls import path

from .views import UserProfileListView, UserProfileDetailView, RegistrationView

urlpatterns = [
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profiles/<str:type>/', UserProfileListView.as_view(), name='user-profile-list'),
     path('registration/', RegistrationView.as_view(), name='registration')
]

