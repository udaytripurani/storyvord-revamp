from rest_framework import serializers
from ..models import (
    ProjectDetails, ProjectRequirements, ShootingDetails, 
    Role, Permission, Membership,
    ProjectCrewRequirement, ProjectEquipmentRequirement, ProjectAISuggestions
)
from accounts.models import Permission as AccountPermission, User
from rest_framework.exceptions import PermissionDenied

# Permission Serializer
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['name', 'description']

# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['name', 'permission', 'description', 'project', 'is_global']

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id')

    class Meta:
        model = User
        fields = ['user_id', 'email']

# Membership Serializer
class MembershipSerializer(serializers.ModelSerializer):
    role = RoleSerializer()
    user = UserSerializer()  # Show the username or other identifier for the user
    membership_id = serializers.IntegerField(source='id')

    class Meta:
        model = Membership
        fields = ['membership_id', 'user', 'role', 'project', 'created_at']
        
        # Project Crew Requirement Serializer
class ProjectCrewRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCrewRequirement
        fields = ['project','crew_title', 'quantity']

# Project Equipment Requirement Serializer
class ProjectEquipmentRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectEquipmentRequirement
        fields = ['project','equipment_title', 'quantity']

# Project Serializer
class ProjectDetailsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()  # Show the username or other identifier for the owner
    members = MembershipSerializer(source='memberships', many=True, read_only=True)
    
    class Meta:
        model = ProjectDetails
        fields = ['project_id', 'owner', 'members', 'name', 'content_type', 'brief', 'additional_details', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        create_project_permission = AccountPermission.objects.get(name='create_project')
        user_type = user.user_type
        
        if user_type is None or not user_type.permissions.filter(id=create_project_permission.id).exists():
            raise PermissionDenied("You don't have permission to create a project.")
        
        validated_data['owner'] = user
        
        # Create the project
        project = ProjectDetails.objects.create(**validated_data)
        
        admin_role = Role.objects.filter(name='admin').first()  # Adjust the role name as necessary
        
        if admin_role:
            Membership.objects.create(user=user, role=admin_role, project=project)
        
        return project


# Project Requirements Serializer
class ProjectRequirementsSerializer(serializers.ModelSerializer):
    crew_requirements = ProjectCrewRequirementSerializer(many=True, read_only=True)
    equipment_requirements = ProjectEquipmentRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectRequirements
        fields = ['id','project', 'budget_currency', 'budget', 'crew_requirements', 'equipment_requirements', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        return ProjectRequirements.objects.create(**validated_data)


# Shooting Details Serializer
class ShootingDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ShootingDetails
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
        }
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        return ShootingDetails.objects.create(**validated_data)
    
class ProjectAISuggestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAISuggestions
        fields = '__all__'