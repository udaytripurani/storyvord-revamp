# Generated by Django 5.1.3 on 2024-11-27 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0003_alter_announcement_project_projectannouncement_and_more'),
        ('project', '0016_alter_projectaisuggestions_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectannouncement',
            name='message',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='projectannouncement',
            name='recipients',
            field=models.ManyToManyField(
                related_name='project_announcements',
                through='announcement.ProjectAnnouncementRecipient',
                to='project.membership',
            ),
        ),
        migrations.AlterField(
            model_name='projectannouncement',
            name='title',
            field=models.CharField(default='Untitled Announcement', max_length=255),
        ),
    ]
