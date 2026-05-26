# jobs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job-list'),
    path('jobs/<slug:slug>/', views.job_detail_view, name='job-detail'),
    path('jobs/<int:job_id>/save/', views.save_job_view, name='save-job'),
]
