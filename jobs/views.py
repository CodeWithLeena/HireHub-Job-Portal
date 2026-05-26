"""
jobs/views.py - Web Views for Jobs
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.text import slugify
from .models import Job, SavedJob
from companies.models import Company


def home_view(request):
    """Homepage - featured jobs + search"""
    featured_jobs = Job.objects.filter(
        is_active=True, status='active',
        is_featured=True, company__status='approved'
    ).select_related('company')[:6]

    recent_jobs = Job.objects.filter(
        is_active=True, status='active', company__status='approved'
    ).select_related('company').order_by('-created_at')[:12]

    featured_companies = Company.objects.filter(
        status='approved', is_featured=True
    )[:6]

    context = {
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
        'featured_companies': featured_companies,
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_companies': Company.objects.filter(status='approved').count(),
    }
    return render(request, 'jobs/home.html', context)


def job_list_view(request):
    """Job listing page with search and filters"""
    qs = Job.objects.filter(
        is_active=True, status='active', company__status='approved'
    ).select_related('company').order_by('-is_featured', '-created_at')

    # Search
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(skills_required__icontains=q) |
            Q(company__name__icontains=q) | Q(location__icontains=q)
        )

    # Filters
    job_type = request.GET.get('job_type')
    work_mode = request.GET.get('work_mode')
    experience = request.GET.get('experience')
    location_filter = request.GET.get('location')

    if job_type:
        qs = qs.filter(job_type=job_type)
    if work_mode:
        qs = qs.filter(work_mode=work_mode)
    if experience:
        qs = qs.filter(experience_required=experience)
    if location_filter:
        qs = qs.filter(
            Q(city__icontains=location_filter) | Q(state__icontains=location_filter)
        )

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'q': q,
        'job_type': job_type,
        'work_mode': work_mode,
        'experience': experience,
        'location_filter': location_filter,
        'total_results': qs.count(),
        'job_type_choices': Job.TYPE_CHOICES,
        'work_mode_choices': Job.WORK_MODE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, slug):
    """Job detail + apply button"""
    job = get_object_or_404(Job, slug=slug, is_active=True)
    Job.objects.filter(pk=job.pk).update(views_count=job.views_count + 1)

    has_applied = False
    is_saved = False

    if request.user.is_authenticated:
        from applications.models import Application
        has_applied = Application.objects.filter(
            applicant=request.user, job=job
        ).exists()
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()

    context = {
        'job': job,
        'has_applied': has_applied,
        'is_saved': is_saved,
        'similar_jobs': Job.objects.filter(
            company=job.company, is_active=True
        ).exclude(pk=job.pk)[:3]
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def save_job_view(request, job_id):
    """Toggle save/unsave a job"""
    job = get_object_or_404(Job, id=job_id)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
        messages.info(request, 'Job removed from saved list.')
    else:
        messages.success(request, 'Job saved successfully!')
    return redirect('job-detail', slug=job.slug)


# --- Job URLs ---
# jobs/urls.py (included in this file for convenience)
