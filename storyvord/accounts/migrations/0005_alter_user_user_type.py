# Generated by Django 5.0.6 on 2024-10-04 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_steps'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('client', 'Client'),
                    ('crew', 'Crew'),
                    ('vendor', 'Vendor'),
                    ('internal', 'Internal Team'),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
