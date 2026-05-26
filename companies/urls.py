# companies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_list_view, name='company-list'),
    path('register/', views.register_company_view, name='register-company'),
    path('mine/', views.my_company_view, name='my-company'),
    path('post-job/', views.post_job_view, name='post-job'),
    path('<slug:slug>/', views.company_detail_view, name='company-detail'),
]
