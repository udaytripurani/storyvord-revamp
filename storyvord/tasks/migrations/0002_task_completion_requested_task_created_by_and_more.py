# Generated by Django 5.0.6 on 2024-07-09 20:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completion_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='created_by',
            field=models.ForeignKey(
                default='',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_tasks',
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='requester',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='requested_tasks',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]