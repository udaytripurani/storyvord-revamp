# Generated by Django 5.0.6 on 2024-08-16 21:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0006_alter_clientcompanyevent_calendar'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('positions', models.TextField(blank=True, null=True)),
                ('on_set', models.BooleanField(default=False)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('secondary_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_office', models.CharField(blank=True, max_length=20, null=True)),
                ('phone_work', models.CharField(blank=True, max_length=20, null=True)),
                ('phone_home', models.CharField(blank=True, max_length=20, null=True)),
                ('phone_private', models.CharField(blank=True, max_length=20, null=True)),
                (
                    'company',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='client.clientcompanyprofile',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]