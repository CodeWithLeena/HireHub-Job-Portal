# applications/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('apply/', api_views.ApplyForJobAPIView.as_view(), name='api-apply'),
    path('mine/', api_views.MyApplicationsAPIView.as_view(), name='api-my-applications'),
    path('company/<int:job_id>/', api_views.CompanyApplicationsAPIView.as_view(), name='api-company-applications'),
    path('<int:pk>/status/', api_views.UpdateApplicationStatusAPIView.as_view(), name='api-update-status'),
    path('<int:pk>/withdraw/', api_views.withdraw_application, name='api-withdraw'),
]


# applications/urls.py (web views - placeholder)
# Add web view urls here if needed
