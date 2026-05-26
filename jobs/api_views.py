"""
jobs/api_views.py - REST API Views for Jobs
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.text import slugify
from django.db.models import Q
from .models import Job, SavedJob
from .serializers import JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer, SavedJobSerializer
from companies.models import Company


class JobListAPIView(generics.ListAPIView):
    """
    GET /api/jobs/
    - Search by title, skills, location
    - Filter by job_type, work_mode, experience_required
    - Order by: -created_at, salary_min, salary_max
    """
    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'skills_required', 'location', 'city', 'company__name']
    ordering_fields = ['created_at', 'salary_min', 'salary_max', 'views_count']
    ordering = ['-is_featured', '-created_at']

    def get_queryset(self):
        qs = Job.objects.filter(is_active=True, status='active',
                                company__status='approved').select_related('company')

        # Filters
        job_type = self.request.query_params.get('job_type')
        work_mode = self.request.query_params.get('work_mode')
        experience = self.request.query_params.get('experience')
        location = self.request.query_params.get('location')
        salary_min = self.request.query_params.get('salary_min')
        salary_max = self.request.query_params.get('salary_max')

        if job_type:
            qs = qs.filter(job_type=job_type)
        if work_mode:
            qs = qs.filter(work_mode=work_mode)
        if experience:
            qs = qs.filter(experience_required=experience)
        if location:
            qs = qs.filter(Q(city__icontains=location) | Q(state__icontains=location) |
                           Q(location__icontains=location))
        if salary_min:
            qs = qs.filter(salary_min__gte=salary_min)
        if salary_max:
            qs = qs.filter(salary_max__lte=salary_max)

        return qs


class JobDetailAPIView(generics.RetrieveAPIView):
    """GET /api/jobs/<slug>/"""
    serializer_class = JobDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related('company')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Job.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class JobCreateAPIView(generics.CreateAPIView):
    """POST /api/jobs/create/ - Only approved employers"""
    serializer_class = JobCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_employer:
            raise PermissionError("Only employers can post jobs.")
        try:
            company = Company.objects.get(owner=user, status='approved')
        except Company.DoesNotExist:
            raise PermissionError("You need an approved company to post jobs.")

        title = serializer.validated_data['title']
        slug = slugify(title)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Job.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        serializer.save(posted_by=user, company=company, slug=slug)


class JobUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """PUT/PATCH/DELETE /api/jobs/<id>/manage/"""
    serializer_class = JobCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user)


class MyJobsAPIView(generics.ListAPIView):
    """GET /api/jobs/mine/ - Company's own job listings"""
    serializer_class = JobListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user).select_related('company')


class SavedJobsAPIView(generics.ListCreateAPIView):
    """
    GET /api/jobs/saved/ - List saved jobs
    POST /api/jobs/saved/ - Save a job
    """
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related('job', 'job__company')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unsave_job(request, job_id):
    """DELETE /api/jobs/saved/<job_id>/unsave/"""
    try:
        saved = SavedJob.objects.get(user=request.user, job_id=job_id)
        saved.delete()
        return Response({'message': 'Job removed from saved.'}, status=status.HTTP_204_NO_CONTENT)
    except SavedJob.DoesNotExist:
        return Response({'error': 'Job not in saved list.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_jobs(request):
    """GET /api/jobs/featured/ - 6 featured jobs for homepage"""
    jobs = Job.objects.filter(
        is_active=True, status='active',
        is_featured=True, company__status='approved'
    ).select_related('company')[:6]
    serializer = JobListSerializer(jobs, many=True, context={'request': request})
    return Response(serializer.data)
