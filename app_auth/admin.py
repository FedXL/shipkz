from django.contrib import admin
from app_auth.models import CustomUser, Profile


@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    list_display = ['username', 'email', 'email_verified']

@admin.register(Profile)
class AdminProfile(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'patronymic_name','phone','email','telegram_id']
    raw_id_fields = ['telegram_user', 'web_user']
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'