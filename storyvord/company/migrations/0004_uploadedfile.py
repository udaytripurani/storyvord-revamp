# Generated by Django 5.0.6 on 2024-08-30 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_clientcompanytask'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('file', models.FileField(upload_to='uploads/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]