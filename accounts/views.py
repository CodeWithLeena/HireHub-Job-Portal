"""
accounts/views.py - Django Web Views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import RegisterSerializer

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'jobseeker')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        elif role == 'admin':
            messages.error(request, 'Invalid role selected.')
        else:
            user = User.objects.create_user(
                email=email, password=password,
                first_name=first_name, last_name=last_name, role=role
            )
            if role == 'jobseeker':
                Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Account created.')
            return redirect('dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}

    if user.is_jobseeker:
        from applications.models import Application
        applications = Application.objects.filter(
            applicant=user
        ).select_related('job', 'job__company').order_by('-applied_at')[:5]
        context['applications'] = applications
        context['total_applications'] = Application.objects.filter(applicant=user).count()

    elif user.is_employer:
        from companies.models import Company
        from jobs.models import Job
        from applications.models import Application
        try:
            company = Company.objects.get(owner=user)
            context['company'] = company
            if company.is_approved:
                recent_jobs = Job.objects.filter(company=company).order_by('-created_at')[:5]
                recent_apps = Application.objects.filter(
                    job__company=company
                ).select_related('applicant', 'job').order_by('-applied_at')[:5]
                context['recent_jobs'] = recent_jobs
                context['recent_applications'] = recent_apps
                context['total_jobs'] = Job.objects.filter(company=company).count()
                context['total_applications'] = Application.objects.filter(
                    job__company=company
                ).count()
        except Company.DoesNotExist:
            context['no_company'] = True

    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update User fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()

        # Update Profile fields
        profile.headline = request.POST.get('headline', '')
        profile.bio = request.POST.get('bio', '')
        profile.skills = request.POST.get('skills', '')
        profile.experience_level = request.POST.get('experience_level', 'fresher')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.linkedin = request.POST.get('linkedin', '')
        profile.github = request.POST.get('github', '')
        profile.portfolio = request.POST.get('portfolio', '')
        profile.is_available = request.POST.get('is_available') == 'on'

        if 'resume' in request.FILES:
            from django.utils import timezone
            profile.resume = request.FILES['resume']
            profile.resume_uploaded_at = timezone.now()
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'accounts/edit_profile.html', {'profile': profile})
