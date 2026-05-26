"""
accounts/api_views.py
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer
)
from .models import Profile

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterAPIView(generics.CreateAPIView):
    """POST /api/accounts/register/"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful!',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutAPIView(APIView):
    """POST /api/accounts/logout/ - Blacklist refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(generics.RetrieveAPIView):
    """GET /api/accounts/me/ - Current user info"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileAPIView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/accounts/profile/"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordAPIView(APIView):
    """POST /api/accounts/change-password/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Incorrect password.'}, status=400)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=400)
