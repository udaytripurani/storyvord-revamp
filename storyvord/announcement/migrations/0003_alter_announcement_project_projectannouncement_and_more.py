# Generated by Django 5.1.3 on 2024-11-26 09:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0002_alter_announcement_recipients'),
        ('project', '0016_alter_projectaisuggestions_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
            ),
        ),
        migrations.CreateModel(
            name='ProjectAnnouncement',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'title',
                    models.CharField(blank=True, default='Untitled Announcement', max_length=255),
                ),
                ('message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_urgent', models.BooleanField(db_index=True, default=False)),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Project Announcement',
                'verbose_name_plural': 'Project Announcements',
            },
        ),
        migrations.CreateModel(
            name='ProjectAnnouncementRecipient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('role', models.CharField(blank=True, max_length=100, null=True)),
                ('is_read', models.BooleanField(default=False)),
                (
                    'membership',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='project.membership'
                    ),
                ),
                (
                    'project_announcement',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='announcement.projectannouncement',
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='projectannouncement',
            name='recipients',
            field=models.ManyToManyField(
                blank=True,
                related_name='project_announcements',
                through='announcement.ProjectAnnouncementRecipient',
                to='project.membership',
            ),
        ),
    ]