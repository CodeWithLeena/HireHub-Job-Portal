"""
accounts/models.py - Custom User Model + Profile
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for HireHub User model"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    Roles: jobseeker | employer | admin
    """
    ROLE_CHOICES = [
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    ]

    # Core fields
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')

    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Profile image
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_employer(self):
        return self.role == 'employer'

    @property
    def is_jobseeker(self):
        return self.role == 'jobseeker'

    @property
    def is_admin_user(self):
        return self.role == 'admin'


class Profile(models.Model):
    """
    Extended profile for Job Seekers
    """
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher (0 years)'),
        ('junior', 'Junior (1-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior (5-10 years)'),
        ('lead', 'Lead (10+ years)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Professional info
    headline = models.CharField(max_length=120, blank=True,
                                help_text="E.g., Full Stack Developer | Django Expert")
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text="Comma separated: Python, Django, React")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES,
                                        default='fresher')
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Resume
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_uploaded_at = models.DateTimeField(null=True, blank=True)

    # Links
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)

    # Location
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, default='India')

    # Meta
    is_available = models.BooleanField(default=True, help_text="Available for opportunities?")
    profile_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def resume_filename(self):
        if self.resume:
            return self.resume.name.split('/')[-1]
        return None
