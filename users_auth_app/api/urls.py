
from django.contrib import admin
from django.urls import path

from .views import UserProfileListView, UserProfileDetailView

urlpatterns = [
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profiles/<str:type>/', UserProfileListView.as_view(), name='userprofile-list'),
]

