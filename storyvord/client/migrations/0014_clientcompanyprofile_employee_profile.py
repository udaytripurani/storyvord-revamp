# Generated by Django 5.0.6 on 2024-12-11 17:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0013_rename_cityandstate_clientcompanyprofile_city_and_state_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='clientcompanyprofile',
            name='employee_profile',
            field=models.ManyToManyField(
                blank=True, related_name='companies', to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
