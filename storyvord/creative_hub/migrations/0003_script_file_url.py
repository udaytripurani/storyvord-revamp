# Generated by Django 5.1.3 on 2024-12-30 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creative_hub', '0002_script_file_alter_script_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='file_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]