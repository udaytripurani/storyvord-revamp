# Generated by Django 5.1.3 on 2025-01-23 07:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_alter_tier_name_alter_tier_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tier',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='accounts.tier',
            ),
        ),
    ]
