"""
accounts/serializers.py - DRF Serializers
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token with extra user info"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.get_full_name(),
            'role': self.user.role,
        }
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """User Registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if data.get('role') == 'admin':
            raise serializers.ValidationError({"role": "Cannot register as admin."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Auto-create profile for job seekers
        if user.role == 'jobseeker':
            Profile.objects.create(user=user)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    skills_list = serializers.ReadOnlyField(source='get_skills_list')

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user', 'profile_views', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'phone', 'avatar', 'is_verified', 'date_joined', 'profile']
        read_only_fields = ['email', 'role', 'is_verified', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return data
