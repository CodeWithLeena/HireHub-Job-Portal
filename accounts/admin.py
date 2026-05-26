"""
Admin Panel registrations for all HireHub models
accounts/admin.py
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'role', 'is_active', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_active', 'is_verified', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'experience_level', 'city', 'is_available', 'profile_views']
    list_filter = ['experience_level', 'is_available', 'country']
    search_fields = ['user__email', 'user__first_name', 'headline', 'skills']
    raw_id_fields = ['user']
