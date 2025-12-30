"""
URL Configuration for Analytics Dashboard
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Set admin site URL to frontend
admin.site.site_url = settings.FRONTEND_URL

# Admin site customization
admin.site.site_header = 'Analytics Dashboard Admin'
admin.site.site_title = 'Analytics Admin'
admin.site.index_title = 'Administration'

urlpatterns = [
    # Admin - uses configurable URL path from settings
    path(settings.ADMIN_URL, admin.site.urls),

    # API v1 Endpoints (versioned)
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/procurement/', include('apps.procurement.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),

    # Legacy API endpoints (for backwards compatibility, will be deprecated)
    path('api/auth/', include('apps.authentication.urls')),
    path('api/procurement/', include('apps.procurement.urls')),
    path('api/analytics/', include('apps.analytics.urls')),

    # API Documentation (only in development)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
