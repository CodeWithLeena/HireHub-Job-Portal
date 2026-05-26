"""
companies/admin.py
"""
from django.contrib import admin
from django.utils import timezone
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'industry', 'size', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'size', 'is_featured', 'country']
    search_fields = ['name', 'owner__email', 'industry']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    actions = ['approve_companies', 'reject_companies', 'suspend_companies']

    def approve_companies(self, request, queryset):
        queryset.update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{queryset.count()} companies approved.')
    approve_companies.short_description = "✅ Approve selected companies"

    def reject_companies(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} companies rejected.')
    reject_companies.short_description = "❌ Reject selected companies"

    def suspend_companies(self, request, queryset):
        queryset.update(status='suspended')
        self.message_user(request, f'{queryset.count()} companies suspended.')
    suspend_companies.short_description = "⛔ Suspend selected companies"
