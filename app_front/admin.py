from django.contrib import admin
from app_front.models import CallbackForm


@admin.register(CallbackForm)
class AdminCallbackForm(admin.ModelAdmin):
    list_display = ['email', 'connect', 'name', 'message']