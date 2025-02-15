# Generated by Django 5.1.3 on 2024-11-22 09:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_remove_projectcrewrequirement_crew_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAISuggestions',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'suggested_budget',
                    models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
                ),
                ('suggested_compliance', models.TextField(blank=True, null=True)),
                ('suggested_culture', models.TextField(blank=True, null=True)),
                ('suggested_logistics', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'project',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='project.project'
                    ),
                ),
                (
                    'shoot',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.shootingdetails'
                    ),
                ),
            ],
        ),
    ]
