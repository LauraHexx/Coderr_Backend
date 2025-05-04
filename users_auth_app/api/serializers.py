from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from users_auth_app.models import UserProfile


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=[('customer', 'Customer'), ('business', 'Business')]
    )

    def validate(self, data):
        """Validate password match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"password": "passwords don't match"})
        return data

    def create(self, validated_data):
        """Create and return a new user with a profile and token."""
        user = self._create_user(validated_data)
        self._set_user_names(user, validated_data['username'])
        user_profile = self._create_user_profile(user, validated_data)
        token = self._create_token(user)

        return self._build_response(user, token)

    def _create_user(self, validated_data):
        """Create a user instance."""
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

    def _set_user_names(self, user, username):
        """Set the first and last name from the username."""
        username_split = username.split(' ')
        user.first_name = username_split[0]
        user.last_name = ' '.join(username_split[1:]) if len(
            username_split) > 1 else ''
        user.save()

    def _create_user_profile(self, user, validated_data):
        """Create a user profile instance."""
        return UserProfile.objects.create(
            user=user,
            type=validated_data['type']
        )

    def _create_token(self, user):
        """Create a token for the user."""
        return Token.objects.create(user=user)

    def _build_response(self, user, token):
        """Build the response data."""
        return {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }


class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description', 'working_hours', 'type', 'email', 'created_at']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'username', 'type', 'created_at']
