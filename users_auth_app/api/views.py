
import datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from users_auth_app.models import UserProfile
from .serializers import RegistrationSerializer, UserProfileDetailSerializer, BusinessUserProfileSerializer, CustomerUserProfileSerializer
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
    and handles guest user registration if necessary.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user login or guest user registration.
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if username in ["andrey", "kevin"]:
            user = self._register_guest_user(username, password)
        else:
            user = self._authenticate_user(username, password)
            if not user:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        return self._generate_token_response(user)

    def _register_guest_user(self, username, password):
        """
        Registers a guest user with a unique username and email.
        """
        unique_number = self._generate_unique_number()
        new_username = f"{username}_{unique_number}"
        new_email = f"guest{unique_number}@example.com"
        profile_type = "customer" if username == "andrey" else "business"

        user = User.objects.create_user(
            username=new_username,
            password=password,
            email=new_email
        )
        self._create_user_profile(user, profile_type)
        return user

    def _authenticate_user(self, username, password):
        """
        Authenticates a regular user.
        """
        return authenticate(username=username, password=password)

    def _generate_unique_number(self):
        """
        Generates a unique number based on the current time.
        """
        now = datetime.datetime.now()
        return now.strftime("%H%M%S")

    def _create_user_profile(self, user, profile_type):
        """
        Creates a user profile for the given user.
        """
        UserProfile.objects.create(
            user=user,
            type=profile_type,
            description=f"Auto-generated profile for {profile_type} guest user."
        )

    def _generate_token_response(self, user):
        """
        Generates a token and response data for the user.
        """
        token, created = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        }
        return Response(data, status=status.HTTP_200_OK)


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
        profile = get_object_or_404(UserProfile, user_id=pk)
        serializer = UserProfileDetailSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Updates a user profile with the provided data for a given profile ID.
        Returns a success response with updated profile data, or errors if validation fails.
        """
        profile = get_object_or_404(UserProfile, user_id=pk)
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
    Raises 400 for invalid profile types.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves a list of user profiles filtered by profile type ('business' or 'customer').
        Raises a 400 error if an invalid profile type is provided.
        """
        profile_type = self.kwargs.get('type')
        if profile_type not in ['business', 'customer']:
            raise ValidationError({"detail": "Invalid profile type"})
        return UserProfile.objects.filter(type=profile_type)

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the profile type.
        """
        profile_type = self.kwargs.get('type')
        if profile_type == 'business':
            return BusinessUserProfileSerializer
        elif profile_type == 'customer':
            return CustomerUserProfileSerializer
        raise ValidationError({"detail": "Invalid profile type"})
