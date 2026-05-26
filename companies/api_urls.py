# companies/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.CompanyListAPIView.as_view(), name='api-company-list'),
    path('register/', api_views.CompanyCreateAPIView.as_view(), name='api-company-register'),
    path('mine/', api_views.MyCompanyAPIView.as_view(), name='api-my-company'),
    path('<slug:slug>/', api_views.CompanyDetailAPIView.as_view(), name='api-company-detail'),
]
