"""
HireHub URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # App URLs (Web Views)
    path('', include('jobs.urls')),
    path('accounts/', include('accounts.urls')),
    path('companies/', include('companies.urls')),
    path('applications/', include('applications.urls')),

    # REST API
    path('api/', include([
        path('accounts/', include('accounts.api_urls')),
        path('jobs/', include('jobs.api_urls')),
        path('companies/', include('companies.api_urls')),
        path('applications/', include('applications.api_urls')),
    ])),
]

# Serve media in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin panel customization
admin.site.site_header = "HireHub Admin"
admin.site.site_title = "HireHub Admin Portal"
admin.site.index_title = "Welcome to HireHub Administration"
