"""
accounts/api_urls.py
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views
from .api_views import CustomTokenObtainPairView

urlpatterns = [
    # Auth
    path('register/', api_views.RegisterAPIView.as_view(), name='api-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='api-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='api-logout'),

    # Profile
    path('me/', api_views.UserProfileAPIView.as_view(), name='api-me'),
    path('profile/', api_views.UpdateProfileAPIView.as_view(), name='api-profile-update'),
    path('change-password/', api_views.ChangePasswordAPIView.as_view(), name='api-change-password'),
]
