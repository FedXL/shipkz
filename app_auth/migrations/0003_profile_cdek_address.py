from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0002_profile_email'),
    ]
    operations = [
        migrations.AddField(
            model_name='profile',
            name='cdek_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
