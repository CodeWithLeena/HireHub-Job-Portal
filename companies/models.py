"""
companies/models.py - Company Model
"""
from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Company profile - linked to an Employer user
    Must be approved by Admin before posting jobs
    """
    SIZE_CHOICES = [
        ('startup', 'Startup (1-10)'),
        ('small', 'Small (11-50)'),
        ('medium', 'Medium (51-200)'),
        ('large', 'Large (201-1000)'),
        ('enterprise', 'Enterprise (1000+)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    # Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies'
    )

    # Basic Info
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='startup')
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)

    # Branding
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    banner = models.ImageField(upload_to='company_banners/', null=True, blank=True)
    website = models.URLField(blank=True)

    # Location
    headquarters = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, default='India')

    # Social
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    # Admin control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_companies'
    )

    # Meta
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def total_jobs(self):
        return self.jobs.filter(is_active=True).count()

    @property
    def total_applicants(self):
        from applications.models import Application
        return Application.objects.filter(job__company=self).count()
