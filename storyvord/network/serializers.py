# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Connection, ActiveConnection

User = get_user_model()

# Serializer for User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

# Serializer for Connection
class ConnectionSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = ['id', 'requester', 'receiver', 'status', 'created_at', 'updated_at']

# Serializer for ActiveConnection
class ActiveConnectionSerializer(serializers.ModelSerializer):
    user_id_1 = UserSerializer(read_only=True)
    user_id_2 = UserSerializer(read_only=True)

    class Meta:
        model = ActiveConnection
        fields = ['id', 'user_id_1', 'user_id_2', 'connected_at']
