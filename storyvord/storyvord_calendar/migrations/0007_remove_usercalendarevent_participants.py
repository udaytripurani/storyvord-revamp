# Generated by Django 5.0.6 on 2024-11-21 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storyvord_calendar', '0006_usercalender_usercalendarevent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercalendarevent',
            name='participants',
        ),
    ]
