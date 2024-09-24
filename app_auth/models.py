from django.contrib.auth.models import User
from django.db import models






class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    birth_date = models.DateField
    telegram_id = models.BigIntegerField()
