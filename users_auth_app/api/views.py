
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from users_auth_app.models import UserProfile
from .serializers import UserProfileListSerializer, UserProfileDetailSerializer, RegistrationSerializer
from .permissions import ReadOnlyOrOwnerUpdateOrAdmin


class RegistrationView(APIView):
    """
    API view for registering a new user.
    Accepts POST requests with user data, validates it,
    and creates a new user account if valid.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user registration by validating and saving the provided data.
        Returns a success response with user data upon successful registration, or errors if validation fails.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(ObtainAuthToken):
    """
    API view for authenticating users.
    Accepts POST requests with username and password,
    and returns an authentication token on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user login by validating the provided credentials and returning an authentication token.
        Returns a success response with the token and user data, or errors if authentication fails.
        """
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            data = {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(APIView):
    """
    API view for retrieving or partially updating a single user profile.
    Requires authentication and proper permissions (owner or admin).
    """
    permission_classes = [IsAuthenticated, ReadOnlyOrOwnerUpdateOrAdmin]

    def get(self, request, pk):
        """
        Retrieves the user profile details for a given profile ID.
        Returns a success response with profile data or a 404 error if not found.
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        serializer = UserProfileDetailSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Updates a user profile with the provided data for a given profile ID.
        Returns a success response with updated profile data, or errors if validation fails.
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        self.check_object_permissions(request, profile)
        serializer = UserProfileDetailSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(ListAPIView):
    """
    API view for listing user profiles by type ('business' or 'customer').
    Only accessible to authenticated users.
    Raises 404 for invalid profile types.
    """
    serializer_class = UserProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves a list of user profiles filtered by profile type ('business' or 'customer').
        Raises a 404 error if an invalid profile type is provided.
        """
        profile_type = self.kwargs['type']

        if profile_type not in ['business', 'customer']:
            raise Http404

        return UserProfile.objects.filter(type=profile_type)
