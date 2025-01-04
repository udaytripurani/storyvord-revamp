# Generated by Django 5.1.3 on 2024-12-16 08:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0017_projectdetails_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectaisuggestions',
            name='shoot',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='project.shootingdetails',
            ),
        ),
    ]
