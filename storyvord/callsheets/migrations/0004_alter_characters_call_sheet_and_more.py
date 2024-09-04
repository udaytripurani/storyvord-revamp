# Generated by Django 5.0.6 on 2024-08-30 15:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callsheets', '0003_remove_callsheet_additional_details_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characters',
            name='call_sheet',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='characters',
                to='callsheets.callsheet',
            ),
        ),
        migrations.AlterField(
            model_name='departmentinstructions',
            name='call_sheet',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='department_instructions',
                to='callsheets.callsheet',
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='call_sheet',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='events',
                to='callsheets.callsheet',
            ),
        ),
        migrations.AlterField(
            model_name='extras',
            name='call_sheet',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='extras',
                to='callsheets.callsheet',
            ),
        ),
        migrations.AlterField(
            model_name='scenes',
            name='call_sheet',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='scenes',
                to='callsheets.callsheet',
            ),
        ),
        migrations.AlterField(
            model_name='weather',
            name='call_sheet',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='weather',
                to='callsheets.callsheet',
            ),
        ),
    ]