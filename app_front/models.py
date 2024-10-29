from django.db import models

class CallbackForm(models.Model):
    email = models.EmailField(verbose_name='Почта', blank=False, null=False)
    connect = models.CharField(verbose_name='Предпочтительный способ связи',null=True, blank=True, max_length=100)
    name = models.CharField(verbose_name='Имя', max_length=100, blank=True, null=True)
    message = models.TextField(verbose_name='Что случилось?',blank=False, null=False, max_length=4000)
