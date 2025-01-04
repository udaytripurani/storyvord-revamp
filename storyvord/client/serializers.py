# client/serializers.py
from rest_framework import serializers

from storyvord.utils import Base64FileField
from .models import *
from accounts.models import User
from django.shortcuts import get_object_or_404

class ProfileSerializer(serializers.ModelSerializer):
    image = Base64FileField(required=False, allow_null=True)

    class Meta:
        model = ClientProfile
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields.pop('user', None)

class ClientCompanyProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ClientCompanyProfile
        fields = "__all__"

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)
    class Meta:
        model = Role
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email')  # Including email in the serialized data
    role = RoleSerializer()

    class Meta:
        model = Membership
        fields = ['id', 'user_email', 'role', 'company', 'status', 'joined_at']

class ClientCompanyFolderSerializer(serializers.ModelSerializer):
    files = serializers.StringRelatedField(many=True, required=False)
    allowed_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClientCompanyFolder
        fields = ['id', 'name', 'description', 'icon', 'company', 'files', 'allowed_users', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        allowed_users = validated_data.pop('allowed_users', [])
        if user:
            validated_data['created_by'] = request.user

        folder = ClientCompanyFolder.objects.create(**validated_data)

        if request and hasattr(request, 'user'):
            folder.allowed_users.add(request.user)

        if folder.company:
            company_owner = folder.company.user
            folder.allowed_users.add(company_owner)

        folder.allowed_users.add(*allowed_users)

        return folder

    def update(self, instance, validated_data):
        allowed_users = validated_data.pop('allowed_users', [])
        instance = super().update(instance, validated_data)
        instance.allowed_users.set(allowed_users)
        return instance

class ClientCompanyFileSerializer(serializers.ModelSerializer):
    file = Base64FileField(required=False, allow_null=True)
    class Meta:
        model = ClientCompanyFile
        fields = ['id', 'name', 'file', 'folder']

    def validate(self, data):
        folder = data.get('folder')
        if not folder:
            raise serializers.ValidationError("Folder is required.")
        return data

class ClientCompanyFileUpdateSerializer(serializers.ModelSerializer):
    folder = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ClientCompanyFile
        fields = ['id', 'name', 'file', 'folder']
    
    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        folder = data.get('folder')

        if folder and folder.created_by != user:
            raise serializers.ValidationError("You do not have permission to edit files in this folder.")
        
        return data

class ClientCompanyFolderUpdateSerializer(serializers.ModelSerializer):
    files = ClientCompanyFileSerializer(many=True, required=False)
    allowed_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    add_users = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    remove_users = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = ClientCompanyFolder
        fields = ['id', 'description', 'icon', 'name', 'company', 'files', 'allowed_users', 'add_users', 'remove_users', 'created_by']

    def validate(self, data):
        folder = self.instance
        user = self.context['request'].user

        if 'company' in data:
            raise serializers.ValidationError({"company": "You cannot change the company of a folder."})

        if 'allowed_users' in data:
            raise serializers.ValidationError({"allowed_users": "You cannot update allowed_users field directly. Use 'add_users' and 'remove_users' fields instead."})

        if folder and folder.created_by != user:
            raise serializers.ValidationError({"detail": "You do not have permission to edit this folder."})

        return data

    def update(self, instance, validated_data):
        add_users_ids = validated_data.pop('add_users', [])
        remove_users_ids = validated_data.pop('remove_users', [])

        company = instance.company

        for user_id in add_users_ids:
            if not company.memberships.filter(user=user_id).exists(): 
                    raise PermissionError(f'User {user_id} does not have permission to view folders for this company')
            instance.allowed_users.add(user_id)

        for user_id in remove_users_ids:
            instance.allowed_users.remove(user_id)
        
        if self.context['request'].user not in instance.allowed_users.all():
            instance.allowed_users.add(self.context['request'].user)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('exclude_files'):
            representation.pop('files', None)
        return representation

class ClientCompanyEventSerializer(serializers.ModelSerializer):
    calendar = serializers.PrimaryKeyRelatedField(read_only=True)
    document = Base64FileField(required=False, allow_null=True)

    class Meta:
        model = ClientCompanyEvent
        fields = '__all__'

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        try:
            company_profile = ClientCompanyProfile.objects.get(user=user)
        except ClientCompanyProfile.DoesNotExist:
            raise serializers.ValidationError("Company profile not found for this user.")

        if data.get('start') and data.get('end') and data['start'] >= data['end']:
            raise serializers.ValidationError("The end time must be after the start time.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        participants = validated_data.pop('participants', [])

        company_profile = ClientCompanyProfile.objects.get(user=user)
        calendar, created = ClientCompanyCalendar.objects.get_or_create(company=company_profile)

        validated_data['calendar'] = calendar

        event = ClientCompanyEvent.objects.create(**validated_data)

        event.participants.set(participants)

        return event

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user

        company_profile = ClientCompanyProfile.objects.get(user=user)
        if instance.calendar.company != company_profile:
            raise serializers.ValidationError("You do not have permission to update this event.")

        participants = validated_data.pop('participants', None)
        if participants is not None:
            instance.participants.set(participants)

        validated_data['calendar'] = instance.calendar

        return super().update(instance, validated_data)