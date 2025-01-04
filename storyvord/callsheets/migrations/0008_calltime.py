# Generated by Django 5.0.6 on 2024-12-17 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callsheets', '0007_callsheet_additional_notes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallTime',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=255)),
                ('position', models.CharField(max_length=255)),
                ('calltime', models.TimeField()),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=255)),
                ('remarks', models.TextField(blank=True, null=True)),
                (
                    'call_sheet',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='call_time',
                        to='callsheets.callsheet',
                    ),
                ),
            ],
        ),
    ]
