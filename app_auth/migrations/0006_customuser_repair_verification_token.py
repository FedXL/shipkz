# cat app_auth/migrations/0006_customuser_repair_verification_token.py
# Generated by Django 5.1.1 on 2024-10-28 03:26

from django.db import migrations, models
class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0005_alter_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='repair_verification_token',
            field=models.TextField(blank=True, editable=False, null=True),
        ),
    ]