# serializers.py
from rest_framework import serializers
from .models import Announcement, ProjectAnnouncement
from accounts.models import User

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        
class UserWithSourceSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    source = serializers.CharField()

    def to_representation(self, instance):
        user_data = UserSerializer(instance["user"]).data
        user_data["source"] = instance["source"]
        return user_data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']
        
class ProjectAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAnnouncement
        fields = '__all__'