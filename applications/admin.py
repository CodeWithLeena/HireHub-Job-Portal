"""
applications/admin.py
"""
from django.contrib import admin
from .models import Application, ApplicationStatusHistory


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'rating', 'applied_at']
    list_filter = ['status', 'use_profile_resume']
    search_fields = ['applicant__email', 'job__title', 'job__company__name']
    readonly_fields = ['applied_at', 'updated_at']
    raw_id_fields = ['applicant', 'job']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('applicant', 'job', 'job__company')


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'previous_status', 'new_status', 'changed_by', 'changed_at']
    readonly_fields = ['changed_at']
