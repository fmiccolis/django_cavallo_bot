from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('cavallo/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('api/', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
