# Generated by Django 5.0.6 on 2024-12-16 12:32

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_projectinvite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectinvite',
            unique_together={('project', 'invitee')},
        ),
    ]
