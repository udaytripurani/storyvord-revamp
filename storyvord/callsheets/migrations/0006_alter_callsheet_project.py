# Generated by Django 5.0.6 on 2024-12-03 13:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callsheets', '0005_callsheet_location'),
        ('project', '0016_alter_projectaisuggestions_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callsheet',
            name='project',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='project.projectdetails'
            ),
        ),
    ]
