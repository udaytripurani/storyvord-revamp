# Generated by Django 5.0.6 on 2024-11-24 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crew', '0008_crewprofile_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crewevent',
            name='crew_member',
        ),
        migrations.RemoveField(
            model_name='crewevent',
            name='event',
        ),
        migrations.DeleteModel(
            name='CrewCalendar',
        ),
        migrations.DeleteModel(
            name='CrewEvent',
        ),
    ]
