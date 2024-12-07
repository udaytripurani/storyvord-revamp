from rest_framework import serializers
from .models import File, Folder
from accounts.models import User
from django.shortcuts import get_object_or_404
import base64
from django.core.files.base import ContentFile
from project.models import Membership, ProjectDetails
import uuid


class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FileSerializer(serializers.ModelSerializer):
    file = Base64FileField(required=False, allow_null=True)
    class Meta:
        model = File
        fields = '__all__'

        
class FolderSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)
    allowed_users = serializers.PrimaryKeyRelatedField(queryset=Membership.objects.all(), many=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Folder 
        fields = ['id', 'description', 'icon', 'name', 'project', 'default', 'files', 'allowed_users', 'created_by']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('exclude_files'):
            representation.pop('files', None)
        return representation

    def validate(self, data):
        try:
            project = data.get('project')
            name = data.get('name')

            project = ProjectDetails.objects.get(project_id=project.project_id)

            # if project and Folder.objects.filter(project__project_id=project.project_id, name=name).exists():
            if project and Folder.objects.filter(project = project, name=name).exists():
                raise serializers.ValidationError({"detail": "Folder with the same name already exists in this project."})

            return data
        except Exception as e:
            print(e)
            raise serializers.ValidationError({"detail": "An error occurred."})

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        # Ensure the user creating the folder is in allowed_users
        allowed_users = validated_data.pop('allowed_users', [])
        if user:
            validated_data['created_by'] = user
            validated_data['default'] = False
        
            # Check if the user is part of the project and add them as a member
            project = validated_data.get('project')
            if project:
                # Ensure user has a valid membership
                membership = get_object_or_404(Membership, user=user, project=project.project_id)
                if membership not in allowed_users:
                    allowed_users.append(membership)

        project = validated_data.get('project')

        project = ProjectDetails.objects.get(project_id=project.project_id)    
        validated_data['project'] = project
        
        print(validated_data)

        folder = Folder.objects.create(**validated_data)

        # Assign allowed_users to the folder
        for membership in allowed_users:
            folder.allowed_users.add(membership)

        return folder


        
class FolderUpdateSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)
    allowed_users = serializers.PrimaryKeyRelatedField(queryset=Membership.objects.all(), many=True, required=False)
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Folder 
        fields = ['id', 'description', 'icon', 'name', 'project', 'default', 'files', 'allowed_users', 'created_by']

    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not membership.role.permission.filter(name=permission_name).exists():
            return False
        return True

    def validate(self, data):
        folder = self.instance
        user = self.context['request'].user

        # Prevent changing the project field
        if 'project' in data:
            raise serializers.ValidationError({"project": "You cannot change the project of a folder."})

        # Check if the membership is valid
        if 'allowed_users' in data:
            for membership in data['allowed_users']:
                if membership.project != folder.project:
                    raise serializers.ValidationError({"allowed_users": "Invalid membership."})

        # Check if user is added in allowed_users
        if 'allowed_users' in data:
            if user not in data['allowed_users']:
                membership = get_object_or_404(Membership, user=user, project=folder.project)
                data['allowed_users'].append(membership)
                

        return data
    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('exclude_files'):
            representation.pop('files', None)
        return representation