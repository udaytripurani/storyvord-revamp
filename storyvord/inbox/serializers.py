from rest_framework import serializers
from accounts.models import User
from .models import DialogsModel, MessageModel, RoomModel


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'name']

    def get_name(self, obj):
        profile = getattr(obj, 'clientprofile', None) or getattr(obj, 'crewprofile', None)
        return f"{profile.firstName} {profile.lastName}" if profile else obj.email


class DialogSerializer(serializers.ModelSerializer):
    user1 = UserProfileSerializer(read_only=True)
    user2 = UserProfileSerializer(read_only=True)

    class Meta:
        model = DialogsModel
        fields = ['id', 'user1', 'user2']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    recipient = UserProfileSerializer(read_only=True)

    class Meta:
        model = MessageModel
        fields = ['id', 'sender', 'recipient', 'text', 'read', 'created']
        
class RoomSerializer(serializers.ModelSerializer):
    members = UserProfileSerializer(many=True, read_only=True)

    class Meta:
        model = RoomModel
        fields = ['id', 'name', 'members', 'created_at']

class RoomMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)

    class Meta:
        model = MessageModel
        fields = ['id', 'sender', 'text', 'created']

