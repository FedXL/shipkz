from django.contrib import admin
from django.urls import path, include


admin.site.site_header = 'ShipKZ Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_front.urls')),
    path('auth/', include('app_auth.urls')),
]

