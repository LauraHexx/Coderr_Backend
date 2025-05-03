from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users_auth_app.models import UserProfile


class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']



class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'username', 'type', 'created_at']




class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=[('customer', 'Customer'), ('business', 'Business')])

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "passwords don't match"})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        username_split = validated_data['username'].split(' ')
        if len(username_split) > 1:
            user.first_name = username_split[0]
            user.last_name = ' '.join(username_split[1:])
        else:
            user.first_name = username_split[0]
            user.last_name = ''

        user.save()

        user_profile = UserProfile.objects.create(
            user=user,
            type=validated_data['type']
        )

        token = Token.objects.create(user=user)

        return {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }