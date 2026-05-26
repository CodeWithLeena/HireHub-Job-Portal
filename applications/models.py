"""
applications/models.py - Job Application Model
"""
from django.db import models
from django.conf import settings


class Application(models.Model):
    """
    Job Application - submitted by a job seeker for a specific job
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn by Applicant'),
    ]

    # Relationships
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='applications'
    )

    # Application details
    cover_letter = models.TextField(blank=True,
                                    help_text="Why are you the right candidate?")
    resume = models.FileField(
        upload_to='application_resumes/',
        null=True, blank=True,
        help_text="Upload your latest resume (PDF)"
    )
    use_profile_resume = models.BooleanField(
        default=True,
        help_text="Use resume from profile"
    )

    # Expected salary for this role
    expected_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Notice period
    notice_period = models.CharField(max_length=50, blank=True,
                                     help_text="E.g., Immediate, 30 days, 60 days")

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_updated_at = models.DateTimeField(auto_now=True)

    # Company notes (internal, not visible to applicant)
    company_notes = models.TextField(blank=True)

    # Rejection reason (visible to applicant)
    rejection_reason = models.TextField(blank=True)

    # Interview
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_location = models.CharField(max_length=200, blank=True,
                                          help_text="Video link or address")

    # Rating by company (1-5)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    # Meta
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        unique_together = ['applicant', 'job']  # One application per job per user
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} → {self.job.title}"

    @property
    def status_badge_color(self):
        colors = {
            'pending': 'warning',
            'shortlisted': 'info',
            'interview': 'primary',
            'offer': 'success',
            'hired': 'success',
            'rejected': 'danger',
            'withdrawn': 'secondary',
        }
        return colors.get(self.status, 'secondary')

    def get_resume(self):
        """Return the correct resume - either application-specific or profile resume"""
        if self.use_profile_resume and hasattr(self.applicant, 'profile'):
            return self.applicant.profile.resume
        return self.resume


class ApplicationStatusHistory(models.Model):
    """Track status changes for an application"""
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='status_history'
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"App #{self.application.id}: {self.previous_status} → {self.new_status}"
