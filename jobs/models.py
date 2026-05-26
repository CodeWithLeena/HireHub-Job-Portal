"""
jobs/models.py - Job Posting Model
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Job(models.Model):
    """
    Job listing posted by an approved company
    """
    TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('contract', 'Contract'),
    ]

    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('junior', '1-2 Years'),
        ('mid', '3-5 Years'),
        ('senior', '5-10 Years'),
        ('lead', '10+ Years'),
    ]

    WORK_MODE_CHOICES = [
        ('onsite', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]

    # Ownership
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )

    # Job Details
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    requirements = models.TextField(help_text="Job requirements, one per line")
    responsibilities = models.TextField(blank=True)
    skills_required = models.TextField(help_text="Comma separated: Python, Django, REST API")
    benefits = models.TextField(blank=True, help_text="Benefits, one per line")

    # Job Type & Mode
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='full_time')
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default='onsite')
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES,
                                           default='fresher')

    # Location
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, default='India')

    # Salary
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=5, default='INR')
    is_salary_visible = models.BooleanField(default=True)

    # Applications
    total_openings = models.PositiveIntegerField(default=1)
    application_deadline = models.DateField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Stats
    views_count = models.PositiveIntegerField(default=0)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} @ {self.company.name}"

    @property
    def is_deadline_passed(self):
        if self.application_deadline:
            return timezone.now().date() > self.application_deadline
        return False

    @property
    def total_applications(self):
        return self.applications.count()

    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,.0f} - ₹{self.salary_max:,.0f}"
        elif self.salary_min:
            return f"₹{self.salary_min:,.0f}+"
        return "Not Disclosed"

    def get_skills_list(self):
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    def get_requirements_list(self):
        return [r.strip() for r in self.requirements.split('\n') if r.strip()]

    def get_benefits_list(self):
        return [b.strip() for b in self.benefits.split('\n') if b.strip()]


class SavedJob(models.Model):
    """Bookmarked jobs by job seekers"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"
