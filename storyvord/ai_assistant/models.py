from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    session_id = models.CharField(primary_key=True, editable=False,max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, null=True, blank=True)
    agent = models.ForeignKey('AiAgents', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)
    user_message = models.TextField()
    ai_response = models.TextField()
    embedding = models.JSONField(default=dict)  # Store the embedding as a JSON field
    timestamp = models.DateTimeField(auto_now_add=True)  # When the message was created

    def __str__(self):
        return f"Message in {self.session.session_id} at {self.timestamp}"
    
class AiAgents(models.Model):
    name = models.CharField(max_length=50)
    config = models.JSONField(default=dict, null=True, blank=True)
    context = models.CharField(max_length=1000)
    expertise_in = models.CharField(max_length=1000)