from django.contrib import admin
from app_auth.models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    list_display = ['username', 'email', 'email_verified']

