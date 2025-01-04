from rest_framework import serializers
from .models import Script, Scene, Shot, Sequence, Storyboard
     
class ScriptSerializer(serializers.ModelSerializer):
    file_url = serializers.URLField(required=False, read_only=True)  # Add a URL field for the file if needed

    class Meta:
        model = Script
        fields = ['id', 'user', 'project', 'title', 'content', 'file', 'file_url', 'suggestions', 'uploaded_at', 'updated_at']
        extra_kwargs = {
            'suggestions': {'required': False},  # Optional suggestions field
        }

class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = ['id', 'script', 'scene_name' ,'description', 'location', 'order', 'timeline', 'created_at', 'updated_at']
        extra_kwargs = {
            'timeline': {'required': False},  # Optional field
            'location': {'required': False},  # Optional field
        }

class ShotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shot
        fields = ['id', 'scene', 'description', 'type', 'order', 'done', 'timeline', 'created_at', 'updated_at']


class SequenceSerializer(serializers.ModelSerializer):
    scenes = SceneSerializer(many=True, read_only=True)  # Nested scenes for detail view

    class Meta:
        model = Sequence
        fields = ['id', 'project', 'name', 'description', 'scenes', 'created_at', 'updated_at']
        extra_kwargs = {
            'description': {'required': False},  # Optional field
        }

class StoryboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storyboard
        fields = ['id', 'scene', 'shot', 'image_url', 'created_at', 'updated_at']
        extra_kwargs = {
            'scene': {'required': False},
            'shot': {'required': False},
        }