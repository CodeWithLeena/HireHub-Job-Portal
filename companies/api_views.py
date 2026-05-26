"""
companies/api_views.py
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from django.utils.text import slugify
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.get_full_name')
    total_jobs = serializers.ReadOnlyField()
    total_applicants = serializers.ReadOnlyField()

    class Meta:
        model = Company
        exclude = ['owner', 'approved_by', 'approved_at', 'rejection_reason', 'slug']
        read_only_fields = ['status', 'is_featured', 'created_at', 'updated_at']


class CompanyListAPIView(generics.ListAPIView):
    """GET /api/companies/ - All approved companies"""
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Company.objects.filter(status='approved').order_by('-is_featured', '-created_at')


class CompanyDetailAPIView(generics.RetrieveAPIView):
    """GET /api/companies/<slug>/"""
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Company.objects.filter(status='approved')


class CompanyCreateAPIView(generics.CreateAPIView):
    """POST /api/companies/register/"""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_employer:
            raise PermissionError("Only employers can register companies.")
        name = serializer.validated_data['name']
        slug = slugify(name)
        base_slug = slug
        counter = 1
        while Company.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        serializer.save(owner=user, slug=slug)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data['message'] = 'Company registered! Awaiting admin approval.'
        return response


class MyCompanyAPIView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/companies/mine/"""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Company.objects.get(owner=self.request.user)
        except Company.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("You haven't registered a company yet.")
