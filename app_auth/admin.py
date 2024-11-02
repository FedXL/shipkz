from django.contrib import admin
from app_auth.models import CustomUser, Profile
from app_auth.tasks import repair_password_move_site

def verify_email(modeladmin, request, queryset):
    for user in queryset:
        user.email_verified = True
        user.save()

@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    actions = [verify_email]
    list_display = ['username', 'email','verification_token','email_verified']
    search_fields = ['username', 'email']

def send_move_email(modeladmin, request, queryset):
    for profile in queryset:
        repair_password_move_site.delay(profile.id)


@admin.register(Profile)
class AdminProfile(admin.ModelAdmin):
    actions = [send_move_email]
    list_display = ['user', 'first_name', 'last_name', 'patronymic_name','phone','email','telegram_id']
    raw_id_fields = ['telegram_user', 'web_user']
    search_fields = ['first_name', 'last_name', 'patronymic_name','phone','email','telegram_id']
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'



