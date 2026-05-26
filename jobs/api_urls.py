# jobs/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.JobListAPIView.as_view(), name='api-job-list'),
    path('featured/', api_views.featured_jobs, name='api-featured-jobs'),
    path('create/', api_views.JobCreateAPIView.as_view(), name='api-job-create'),
    path('mine/', api_views.MyJobsAPIView.as_view(), name='api-my-jobs'),
    path('saved/', api_views.SavedJobsAPIView.as_view(), name='api-saved-jobs'),
    path('saved/<int:job_id>/unsave/', api_views.unsave_job, name='api-unsave-job'),
    path('<slug:slug>/', api_views.JobDetailAPIView.as_view(), name='api-job-detail'),
    path('<int:pk>/manage/', api_views.JobUpdateDeleteAPIView.as_view(), name='api-job-manage'),
]
