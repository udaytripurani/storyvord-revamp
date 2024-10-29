from rest_framework import serializers
from .models import ChatMessage
from project.models import ProjectRequirements

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ProjectRequirementsSerializer(serializers.Serializer):

    class Meta:
        model = ProjectRequirements
        fields = '__all__'