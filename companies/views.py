"""
companies/views.py + urls.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Company
from jobs.models import Job


def company_list_view(request):
    companies = Company.objects.filter(status='approved').order_by('-is_featured', '-created_at')
    return render(request, 'companies/company_list.html', {'companies': companies})


def company_detail_view(request, slug):
    company = get_object_or_404(Company, slug=slug, status='approved')
    jobs = Job.objects.filter(company=company, is_active=True).order_by('-created_at')
    return render(request, 'companies/company_detail.html', {'company': company, 'jobs': jobs})


@login_required
def register_company_view(request):
    if not request.user.is_employer:
        messages.error(request, 'Only employers can register companies.')
        return redirect('dashboard')

    if Company.objects.filter(owner=request.user).exists():
        messages.info(request, 'You already have a company registered.')
        return redirect('my-company')

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = slugify(name)
        base_slug = slug
        counter = 1
        while Company.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        company = Company.objects.create(
            owner=request.user,
            name=name,
            slug=slug,
            description=request.POST.get('description', ''),
            industry=request.POST.get('industry', ''),
            size=request.POST.get('size', 'startup'),
            website=request.POST.get('website', ''),
            headquarters=request.POST.get('headquarters', ''),
        )
        if 'logo' in request.FILES:
            company.logo = request.FILES['logo']
            company.save()

        messages.success(request, 'Company registered! Awaiting admin approval.')
        return redirect('dashboard')

    return render(request, 'companies/register_company.html')


@login_required
def my_company_view(request):
    try:
        company = Company.objects.get(owner=request.user)
    except Company.DoesNotExist:
        return redirect('register-company')
    jobs = Job.objects.filter(company=company).order_by('-created_at')
    return render(request, 'companies/my_company.html', {'company': company, 'jobs': jobs})


@login_required
def post_job_view(request):
    try:
        company = Company.objects.get(owner=request.user, status='approved')
    except Company.DoesNotExist:
        messages.error(request, 'You need an approved company to post jobs.')
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        slug = slugify(title)
        base_slug = slug
        counter = 1
        while Job.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        Job.objects.create(
            company=company,
            posted_by=request.user,
            title=title,
            slug=slug,
            description=request.POST.get('description', ''),
            requirements=request.POST.get('requirements', ''),
            responsibilities=request.POST.get('responsibilities', ''),
            skills_required=request.POST.get('skills_required', ''),
            benefits=request.POST.get('benefits', ''),
            job_type=request.POST.get('job_type', 'full_time'),
            work_mode=request.POST.get('work_mode', 'onsite'),
            experience_required=request.POST.get('experience_required', 'fresher'),
            location=request.POST.get('location', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            total_openings=request.POST.get('total_openings', 1),
            application_deadline=request.POST.get('application_deadline') or None,
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('my-company')

    return render(request, 'companies/post_job.html', {'company': company})
