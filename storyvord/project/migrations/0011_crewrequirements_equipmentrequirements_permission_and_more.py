# Generated by Django 5.0.6 on 2024-10-10 07:45

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_alter_onboardrequest_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CrewRequirements',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentRequirements',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ProjectDetails',
            fields=[
                (
                    'project_id',
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ('name', models.CharField(max_length=255)),
                ('content_type', models.CharField(max_length=256)),
                ('brief', models.TextField()),
                ('additional_details', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'members',
                    models.ManyToManyField(
                        blank=True, related_name='project_members', to='project.membership'
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                'ordering': ['project_id'],
            },
        ),
        migrations.CreateModel(
            name='ProjectCrewRequirement',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('quantity', models.PositiveIntegerField()),
                (
                    'crew',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.crewrequirements'
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='membership',
            name='project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='memberships',
                to='project.projectdetails',
            ),
        ),
        migrations.CreateModel(
            name='ProjectEquipmentRequirement',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('quantity', models.PositiveIntegerField()),
                (
                    'equipment',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='project.equipmentrequirements',
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ProjectRequirements',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('budget_currency', models.CharField(default='$', max_length=256)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=14, null=True)),
                ('status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    'crew_requirements',
                    models.ManyToManyField(
                        related_name='projects_with_crew', to='project.crewrequirements'
                    ),
                ),
                (
                    'equipment_requirements',
                    models.ManyToManyField(
                        related_name='projects_with_equipment', to='project.equipmentrequirements'
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='project_requirements',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_global', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'permission',
                    models.ManyToManyField(
                        blank=True, related_name='permission', to='project.permission'
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='roles',
                        to='project.projectdetails',
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='membership_role',
                to='project.role',
            ),
        ),
        migrations.CreateModel(
            name='ShootingDetails',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('location', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                (
                    'mode_of_shooting',
                    models.CharField(
                        choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor'), ('both', 'Both')],
                        max_length=255,
                    ),
                ),
                ('permits', models.BooleanField(default=False)),
                ('ai_suggestion', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='shooting_details',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]