
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from users_auth_app.models import UserProfile
from .serializers import UserProfileListSerializer, UserProfileDetailSerializer, RegistrationSerializer
from .permissions import IsOwnerOrAdmin




class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk)
        serializer = UserProfileDetailSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk)
        serializer = UserProfileDetailSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(ListAPIView):
    serializer_class = UserProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile_type = self.kwargs['type']

        if profile_type not in ['business', 'customer']:
            raise Http404

        return UserProfile.objects.filter(type=profile_type)
    


class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)