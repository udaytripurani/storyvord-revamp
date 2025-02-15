# Generated by Django 5.0.6 on 2024-08-15 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0009_selectcrew_selectequipment_remove_project_equipment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectInvitation',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('crew_email', models.EmailField(max_length=254)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending'),
                            ('accepted', 'Accepted'),
                            ('rejected', 'Rejected'),
                        ],
                        default='pending',
                        max_length=10,
                    ),
                ),
                ('referral_code', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.project'
                    ),
                ),
            ],
        ),
    ]
