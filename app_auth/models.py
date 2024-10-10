import uuid
from django.contrib.auth.models import  AbstractUser
from django.db import models
from legacy.models import Users , WebUsers

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False,null=True)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255,blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100,blank=True, null=True)
    last_name = models.CharField(max_length=100,blank=True, null=True)
    patronymic_name = models.CharField(max_length=100,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cdek_address = models.CharField(max_length=255, blank=True, null=True)

    telegram_user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True, related_name='profile')
    web_user = models.ForeignKey(WebUsers, on_delete=models.CASCADE, blank=True, null=True, related_name='profile')


