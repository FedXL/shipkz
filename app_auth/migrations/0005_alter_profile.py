from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0004_alter_customuser_verification_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
#