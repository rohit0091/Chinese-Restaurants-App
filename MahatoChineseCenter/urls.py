"""
URL configuration for MahatoChineseCenter project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Health probes — CloudSentinel monitors /health/ready every 5 seconds
    path('health/live',  views.health_live,  name='health_live'),
    path('health/ready', views.health_ready, name='health_ready'),
    path('health',       views.health_check, name='health_check'),  # backward compat
    path('app/',         views.app_info,     name='app_info'),      # dashboard traffic test

    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('menu/', include('menu.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
]

# Media files served by Nginx in production; only needed here in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
