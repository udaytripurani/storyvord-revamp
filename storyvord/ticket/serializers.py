from rest_framework import serializers
from .models import Ticket, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # To show username instead of ID

    class Meta:
        model = Comment
        fields = ['id', 'user', 'comment_text', 'visibility', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  # Nested comments
    created_by = serializers.StringRelatedField()  # Shows username of the creator
    assigned_to = serializers.StringRelatedField(allow_null=True)  # Shows username of the assigned agent if available

    class Meta:
        model = Ticket
        fields = [
            'ticket_id', 'title', 'description', 'category', 'priority', 'status',
            'created_by', 'assigned_to', 'created_at', 'updated_at',
            'resolved_at', 'closed_at', 'comments'
        ]
        read_only_fields = ['status', 'created_by', 'created_at', 'updated_at']

from rest_framework import serializers
from .models import Agent

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'email', 'name', 'is_active', 'is_staff', 'created_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only (not returned in responses)
        }

    def create(self, validated_data):
        # Ensure that the password is set properly using set_password
        password = validated_data.pop('password', None)  # Remove the password from validated_data
        agent = super().create(validated_data)  # Create the agent without password
        if password:
            agent.set_password(password)  # Set the hashed password
            agent.save()  # Save the agent with the hashed password
        return agent