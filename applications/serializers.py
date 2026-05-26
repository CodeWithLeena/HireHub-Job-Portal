"""
applications/serializers.py
"""
from rest_framework import serializers
from .models import Application, ApplicationStatusHistory
from accounts.serializers import UserSerializer
from jobs.serializers import JobListSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.ReadOnlyField(source='applicant.get_full_name')
    applicant_email = serializers.ReadOnlyField(source='applicant.email')
    job_title = serializers.ReadOnlyField(source='job.title')
    company_name = serializers.ReadOnlyField(source='job.company.name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    status_badge_color = serializers.ReadOnlyField()

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'applicant_name', 'applicant_email',
            'job', 'job_title', 'company_name',
            'cover_letter', 'resume', 'use_profile_resume',
            'expected_salary', 'notice_period',
            'status', 'status_display', 'status_badge_color',
            'rejection_reason', 'interview_date', 'interview_location',
            'rating', 'applied_at', 'updated_at',
        ]
        read_only_fields = [
            'applicant', 'status', 'rejection_reason',
            'interview_date', 'interview_location', 'rating',
            'applied_at', 'updated_at',
        ]


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """For employers to update application status"""

    class Meta:
        model = Application
        fields = [
            'status', 'company_notes', 'rejection_reason',
            'interview_date', 'interview_location', 'rating',
        ]
