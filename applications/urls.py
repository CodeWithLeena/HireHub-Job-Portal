# applications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('apply/<int:job_id>/', views.apply_job_view, name='apply-job'),
    path('mine/', views.my_applications_view, name='my-applications'),
    path('<int:pk>/', views.application_detail_view, name='application-detail'),
    path('company/job/<int:job_id>/', views.company_applicants_view, name='company-applicants'),
    path('<int:pk>/update-status/', views.update_application_status_view, name='update-app-status'),
]
