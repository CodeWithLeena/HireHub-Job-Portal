"""
jobs/admin.py
"""
from django.contrib import admin
from .models import Job, SavedJob


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'work_mode', 'location',
                    'is_active', 'is_featured', 'views_count', 'created_at']
    list_filter = ['job_type', 'work_mode', 'experience_required', 'is_active',
                   'is_featured', 'status']
    search_fields = ['title', 'company__name', 'skills_required', 'location']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'slug']
    actions = ['activate_jobs', 'deactivate_jobs', 'feature_jobs']

    def activate_jobs(self, request, queryset):
        queryset.update(is_active=True, status='active')
    activate_jobs.short_description = "✅ Activate selected jobs"

    def deactivate_jobs(self, request, queryset):
        queryset.update(is_active=False, status='paused')
    deactivate_jobs.short_description = "⛔ Deactivate selected jobs"

    def feature_jobs(self, request, queryset):
        queryset.update(is_featured=True)
    feature_jobs.short_description = "⭐ Feature selected jobs"


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'saved_at']
    raw_id_fields = ['user', 'job']
