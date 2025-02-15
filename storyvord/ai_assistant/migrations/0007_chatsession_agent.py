# Generated by Django 5.1.3 on 2024-11-20 07:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_assistant', '0006_chatmessage_user_alter_chatsession_session_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='agent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='ai_assistant.aiagents',
            ),
        ),
    ]
