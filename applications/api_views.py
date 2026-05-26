"""
applications/api_views.py - Application REST API
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Application, ApplicationStatusHistory
from .serializers import ApplicationSerializer, ApplicationUpdateSerializer
from jobs.models import Job


class ApplyForJobAPIView(generics.CreateAPIView):
    """
    POST /api/applications/apply/
    Job seeker applies for a job
    """
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_jobseeker:
            return Response({'error': 'Only job seekers can apply.'}, status=400)

        job_id = request.data.get('job')
        try:
            job = Job.objects.get(id=job_id, is_active=True)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found or inactive.'}, status=404)

        if job.is_deadline_passed:
            return Response({'error': 'Application deadline has passed.'}, status=400)

        if Application.objects.filter(applicant=user, job=job).exists():
            return Response({'error': 'You have already applied for this job.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(applicant=user, job=job)

        # Send email notification
        send_application_email(application)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyApplicationsAPIView(generics.ListAPIView):
    """GET /api/applications/mine/ - Job seeker's applications"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__company').order_by('-applied_at')


class CompanyApplicationsAPIView(generics.ListAPIView):
    """GET /api/applications/company/<job_id>/ - Company views applicants"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return Application.objects.filter(
            job_id=job_id,
            job__posted_by=self.request.user
        ).select_related('applicant', 'applicant__profile')


class UpdateApplicationStatusAPIView(generics.UpdateAPIView):
    """
    PATCH /api/applications/<id>/status/
    Company updates application status
    """
    serializer_class = ApplicationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(job__posted_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        response = super().update(request, *args, **kwargs)

        new_status = instance.status

        # Track status history
        ApplicationStatusHistory.objects.create(
            application=instance,
            previous_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            note=request.data.get('note', '')
        )

        # Send email to applicant
        send_status_update_email(instance)

        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_application(request, pk):
    """POST /api/applications/<pk>/withdraw/"""
    try:
        app = Application.objects.get(pk=pk, applicant=request.user)
        if app.status in ['hired', 'rejected']:
            return Response({'error': f'Cannot withdraw a {app.status} application.'}, status=400)
        old_status = app.status
        app.status = 'withdrawn'
        app.save()
        ApplicationStatusHistory.objects.create(
            application=app, previous_status=old_status,
            new_status='withdrawn', changed_by=request.user
        )
        return Response({'message': 'Application withdrawn successfully.'})
    except Application.DoesNotExist:
        return Response({'error': 'Application not found.'}, status=404)


# =====================
# EMAIL UTILITIES
# =====================
def send_application_email(application):
    """Notify applicant and company on new application"""
    try:
        # To applicant
        send_mail(
            subject=f'Application Submitted - {application.job.title}',
            message=f"""
Hi {application.applicant.first_name},

Your application for "{application.job.title}" at {application.job.company.name}
has been successfully submitted!

Application ID: #{application.id}
Status: Pending Review

You can track your application status in your dashboard.

Best of luck!
Team HireHub
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=True
        )

        # To company
        send_mail(
            subject=f'New Application - {application.job.title}',
            message=f"""
Hi {application.job.company.name} Team,

{application.applicant.get_full_name()} has applied for "{application.job.title}".

Review the application in your company dashboard.

Team HireHub
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.job.posted_by.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Email error: {e}")


def send_status_update_email(application):
    """Notify applicant when status changes"""
    status_messages = {
        'shortlisted': 'Congratulations! You have been shortlisted.',
        'interview': f'Your interview is scheduled on {application.interview_date}.',
        'offer': 'An offer has been extended to you!',
        'hired': 'Congratulations! You have been hired!',
        'rejected': 'We regret to inform you that your application was not selected.',
    }

    message = status_messages.get(application.status)
    if not message:
        return

    try:
        send_mail(
            subject=f'Application Update - {application.job.title}',
            message=f"""
Hi {application.applicant.first_name},

Update on your application for "{application.job.title}" at {application.job.company.name}:

{message}

{f'Reason: {application.rejection_reason}' if application.rejection_reason else ''}

Visit your dashboard for more details.

Team HireHub
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Email error: {e}")
