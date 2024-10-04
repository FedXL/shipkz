from django.conf import settings
from django.contrib import admin
from django.urls import path, include


admin.site.site_header = 'ShipKZ Admin'

urlpatterns = [
    path(f'admin/', admin.site.urls),
    path(f'', include('app_front.urls')),
    path(f'auth/', include('app_auth.urls')),
    path(f'__debug__/', include('debug_toolbar.urls')),
]

