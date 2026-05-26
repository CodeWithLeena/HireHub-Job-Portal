"""
applications/views.py + urls.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Application, ApplicationStatusHistory
from jobs.models import Job


@login_required
def apply_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)

    if not request.user.is_jobseeker:
        messages.error(request, 'Only job seekers can apply.')
        return redirect('job-detail', slug=job.slug)

    if Application.objects.filter(applicant=request.user, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job-detail', slug=job.slug)

    if job.is_deadline_passed:
        messages.error(request, 'Application deadline has passed.')
        return redirect('job-detail', slug=job.slug)

    if request.method == 'POST':
        application = Application.objects.create(
            applicant=request.user,
            job=job,
            cover_letter=request.POST.get('cover_letter', ''),
            expected_salary=request.POST.get('expected_salary') or None,
            notice_period=request.POST.get('notice_period', ''),
            use_profile_resume=request.POST.get('use_profile_resume') == 'on',
        )
        if 'resume' in request.FILES and not application.use_profile_resume:
            application.resume = request.FILES['resume']
            application.save()

        # Email notification
        from .api_views import send_application_email
        send_application_email(application)

        messages.success(request, f'Applied for "{job.title}" successfully!')
        return redirect('my-applications')

    return render(request, 'applications/apply.html', {'job': job})


@login_required
def my_applications_view(request):
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__company').order_by('-applied_at')
    return render(request, 'applications/my_applications.html', {'applications': applications})


@login_required
def application_detail_view(request, pk):
    app = get_object_or_404(Application, pk=pk, applicant=request.user)
    history = app.status_history.all()
    return render(request, 'applications/application_detail.html', {'app': app, 'history': history})


@login_required
def company_applicants_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applicants = Application.objects.filter(
        job=job
    ).select_related('applicant', 'applicant__profile').order_by('-applied_at')
    return render(request, 'applications/company_applicants.html', {'job': job, 'applicants': applicants})


@login_required
def update_application_status_view(request, pk):
    app = get_object_or_404(Application, pk=pk, job__posted_by=request.user)
    if request.method == 'POST':
        old_status = app.status
        new_status = request.POST.get('status')
        app.status = new_status
        app.rejection_reason = request.POST.get('rejection_reason', '')
        app.interview_date = request.POST.get('interview_date') or None
        app.interview_location = request.POST.get('interview_location', '')
        app.company_notes = request.POST.get('company_notes', '')
        app.save()

        ApplicationStatusHistory.objects.create(
            application=app, previous_status=old_status,
            new_status=new_status, changed_by=request.user,
            note=request.POST.get('note', '')
        )
        from .api_views import send_status_update_email
        send_status_update_email(app)
        messages.success(request, 'Application status updated.')
    return redirect('company-applicants', job_id=app.job.id)
