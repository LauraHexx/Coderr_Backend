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
        self._create_user_profile(user, validated_data)
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
        try:
            user_profile = UserProfile.objects.create(
                user=user,
                type=validated_data['type']
            )
            print(f"User profile created for user: {user.username}")
            return user_profile
        except Exception as e:
            print(f"Error creating user profile for {user.username}: {e}")
            raise

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


class UserProfileDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(
        source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    created_at = serializers.DateTimeField(
        source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name',
            'file', 'location', 'tel', 'description',
            'working_hours', 'type', 'email', 'created_at',
        ]
        read_only_fields = ['user', 'username', 'type', 'created_at']

    def update(self, instance, validated_data):
        """
        Updates UserProfile and nested User fields (e.g. first_name, email) if provided.
        Handles partial updates by separating and applying user-related data appropriately.
        """
        user_data = validated_data.pop('user', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance


class BusinessUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description', 'working_hours', 'type']


class CustomerUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file',
                  'tel', 'description', 'type']
