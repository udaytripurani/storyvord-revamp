# Generated by Django 4.2.13 on 2024-07-10 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_project_bucket_name_project_project_folder_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='uploaded_document',
            field=models.FileField(blank=True, null=True, upload_to='projects/'),
        ),
    ]