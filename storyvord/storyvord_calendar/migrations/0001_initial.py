# Generated by Django 5.0.6 on 2024-07-06 14:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0005_alter_project_location_details'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=255)),
                (
                    'project',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='calendar',
                        to='project.project',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                (
                    'calendar',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='events',
                        to='storyvord_calendar.calendar',
                    ),
                ),
            ],
        ),
    ]
