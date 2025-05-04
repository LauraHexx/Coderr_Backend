
from django.contrib import admin
from django.urls import path

from .views import UserProfileListView, UserProfileDetailView, RegistrationView, LoginView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(),
         name='user-profile-detail'),
    path('profiles/<str:type>/', UserProfileListView.as_view(),
         name='user-profile-list'),
]
