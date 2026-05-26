"""
jobs/serializers.py - Job DRF Serializers
"""
from rest_framework import serializers
from .models import Job, SavedJob


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for job listings"""
    company_name = serializers.ReadOnlyField(source='company.name')
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    salary_range = serializers.ReadOnlyField()
    total_applications = serializers.ReadOnlyField()
    skills_list = serializers.ReadOnlyField(source='get_skills_list')

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company_name', 'company_logo',
            'job_type', 'work_mode', 'experience_required',
            'location', 'city', 'state',
            'salary_range', 'is_salary_visible',
            'skills_list', 'total_applications',
            'is_featured', 'created_at', 'application_deadline',
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for job detail page"""
    company_name = serializers.ReadOnlyField(source='company.name')
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    company_id = serializers.ReadOnlyField(source='company.id')
    company_description = serializers.ReadOnlyField(source='company.description')
    company_size = serializers.ReadOnlyField(source='company.size')
    salary_range = serializers.ReadOnlyField()
    total_applications = serializers.ReadOnlyField()
    skills_list = serializers.ReadOnlyField(source='get_skills_list')
    requirements_list = serializers.ReadOnlyField(source='get_requirements_list')
    benefits_list = serializers.ReadOnlyField(source='get_benefits_list')
    is_deadline_passed = serializers.ReadOnlyField()

    class Meta:
        model = Job
        exclude = ['posted_by']


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """For employers to create/update jobs"""

    class Meta:
        model = Job
        exclude = ['posted_by', 'company', 'slug', 'views_count', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('salary_min') and data.get('salary_max'):
            if data['salary_min'] > data['salary_max']:
                raise serializers.ValidationError(
                    {"salary_min": "Minimum salary cannot exceed maximum."}
                )
        return data


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), write_only=True, source='job'
    )

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'job_id', 'saved_at']
