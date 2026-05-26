from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from companies.models import Company
from jobs.models import Job
from applications.models import Application
from django.utils.text import slugify
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Generate realistic LinkedIn-style dataset"

    def handle(self, *args, **kwargs):

        self.stdout.write("🧹 Cleaning old data...")
        Application.objects.all().delete()
        Job.objects.all().delete()
        Company.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # ---------------- USERS ----------------
        self.stdout.write("👤 Creating users...")

        first_names = ["Aarav", "Riya", "Kabir", "Ananya", "Vivaan", "Isha", "Aditya", "Neha"]
        last_names = ["Sharma", "Verma", "Gupta", "Singh", "Jain", "Mehta"]

        users = []
        for i in range(20):
           user = User.objects.create_user(
              email=f"user{i}@hirehub.com",
              password="test12345",
              first_name=random.choice(first_names),
              last_name=random.choice(last_names),
              role="jobseeker" if i % 2 == 0 else "employer",
              )
        users.append(user)

        # ---------------- COMPANIES ----------------
        self.stdout.write("🏢 Creating companies...")

        company_names = [
            "Google India", "Microsoft India", "Amazon Development Center",
            "Flipkart", "Zomato", "Swiggy", "TCS", "Infosys",
            "Wipro", "Accenture", "Zoho", "Freshworks"
        ]

        companies = []
        for name in company_names:
           c = Company.objects.create(
               owner=random.choice([u for u in users if u.is_employer]),
               name=name,
               slug=slugify(name),
               tagline=f"{name} Careers",
               description=f"{name} is a leading tech company in India.",
               industry="Information Technology",
               size=random.choice(['startup', 'small', 'medium', 'large']),
               headquarters=random.choice(["Bangalore", "Hyderabad", "Pune"]),
               city=random.choice(["Bangalore", "Hyderabad", "Pune"]),
               state="India",
               website=f"https://{slugify(name)}.com",
               status='approved',
               is_featured=random.choice([True, False]),
               )
           companies.append(c)

        # ---------------- JOBS ----------------
        self.stdout.write("💼 Creating jobs...")

        job_titles = [
            "Software Engineer", "Backend Developer (Django)",
            "Frontend Developer (React)", "Full Stack Engineer",
            "Data Analyst", "Machine Learning Engineer",
            "DevOps Engineer", "QA Engineer"
        ]

        jobs = []
        for i in range(40):
           job = Job.objects.create(
              title=random.choice(job_titles),
              company=random.choice(companies),
              posted_by=random.choice(users),

              description="We are looking for passionate engineers to join our team.",

              requirements="""
              Strong Python knowledge
              Django experience
              REST API understanding
              Git/GitHub
              """,

              responsibilities="""
              Build scalable backend systems
              Collaborate with frontend team
              Write clean code
              """,

              skills_required="Python,Django,REST API,Git",

              benefits="""
Health Insurance
Remote Work
Flexible Hours
""",

              location=random.choice(["Bangalore", "Hyderabad", "Pune", "Delhi", "Remote"]),

              salary_min=random.choice([400000, 600000, 1000000]),
              salary_max=random.choice([800000, 1200000, 2000000]),

              job_type="full_time",

              work_mode=random.choice(["remote", "onsite", "hybrid"]),

              experience_required=random.choice([
        "fresher",
        "junior",
        "mid"
    ]),

              is_featured=random.choice([True, False]),

              slug=f"job-{i}-{random.randint(1000,9999)}"
)
        jobs.append(job)

        # ---------------- APPLICATIONS ----------------
        self.stdout.write("📩 Creating applications...")

        statuses = ["pending", "shortlisted", "interview", "rejected", "hired"]

        for user in users:
            if user.is_jobseeker:
                applied_jobs = random.sample(jobs, k=random.randint(2, 6))

                for job in applied_jobs:
                    Application.objects.create(
                        applicant=user,
                        job=job,
                        status=random.choice(statuses),
                        cover_letter="I am very interested in this role and have relevant experience.",
                        applied_at=timezone.now() - timedelta(days=random.randint(1, 30))
                    )

        self.stdout.write(self.style.SUCCESS("🚀 LinkedIn-style dataset created successfully!"))