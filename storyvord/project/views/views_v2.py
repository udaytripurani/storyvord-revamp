from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from accounts.models import Permission as AccountPermission
from ..models import (
    ProjectDetails, ProjectRequirements, ShootingDetails, 
    Role, Membership, User, Permission,ProjectCrewRequirement, ProjectEquipmentRequirement,
)
from ..serializers.serializers_v2 import (
    ProjectDetailsSerializer, ProjectRequirementsSerializer, ShootingDetailsSerializer, 
    RoleSerializer, MembershipSerializer
)

from project.utils import project_ai_suggestion

# Project Viewset
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = ProjectDetails.objects.all()
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    serializer_class = ProjectDetailsSerializer

    def get_queryset(self):
        """
        Only return projects where the user is either the owner or a member.
        Non-members should not be able to access any project details.
        """
        return ProjectDetails.objects.filter(
            Q(owner=self.request.user) | 
            Q(memberships__user=self.request.user)
        ).distinct()
        
    def get_object(self):
        """
        Override get_object to provide a more specific error when a project is not found or the user doesn't have access.
        """
        try:
            # Check if the project exists and if the user is either the owner or a member
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, pk=self.kwargs.get('pk'))  # Adjust if you're using a different identifier
            return obj
        except ProjectDetails.DoesNotExist:
            # Return a clear error message if the project does not exist or the user has no access
            raise PermissionDenied("You do not have permission to access this project or the project does not exist.")
    
    # Create a custom action for creating a project-specific role
    #TODO need to add permission check here ->
    @action(detail=True, methods=['post'])
    def create_role(self, request, pk=None):
        project = self.get_object()
        data = request.data
        data['project'] = project.id  # Assign the project to the role
        role_serializer = RoleSerializer(data=data)
        if role_serializer.is_valid():
            role_serializer.save()
            return Response(role_serializer.data, status=status.HTTP_201_CREATED)
        return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Action to manage adding/removing members from a project
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        try:
            project = self.get_object()
            
            user = request.data.get('user_id')
            role = request.data.get('role_id')
            
            if not user or not role:
                return Response({'error': 'User and Role are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Membership.objects.filter(project=project, user_id=user).exists():
                    return Response({'error': 'User is already a member of the project'}, status=status.HTTP_400_BAD_REQUEST)

            if request.user == project.owner or Membership.objects.filter(
                project=project, 
                user=request.user,
                role__permission__name='add_members'
            ).exists():
                membership = Membership.objects.create(user_id=user, role_id=role, project=project)
                membership.save()

                return Response({'message': 'Member added successfully'}, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied("You don't have permission to add members to this project.")
            
        except ProjectDetails.DoesNotExist:
            # Return a 404 error if the project doesn't exist or the user has no access
            return Response({'error': 'Project does not exist or you do not have access to it.'}, status=status.HTTP_404_NOT_FOUND)

        except PermissionDenied as e:
            # Catch and return permission-related errors
            return Response({'Permission error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            # General error handling
            return Response({'Exception error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Project Requirements Viewset
class ProjectRequirementsViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequirements.objects.all()
    serializer_class = ProjectRequirementsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        project = get_object_or_404(ProjectDetails, project_id=data.get("project"))

        # Permission check
        if project.owner != user and not Membership.objects.filter(project=project, user=user).exists():
            raise PermissionDenied("You do not have permission to create requirements for this project.")

        # Prepare data for ProjectRequirements
        project_requirements_data = {
            "project": project,
            "budget_currency": data.get("budget_currency", "$"),
            "budget": data.get("budget"),
            "created_by": user,
            "updated_by": user,
        }

        # Create ProjectRequirements instance
        try:
            project_requirements = ProjectRequirements.objects.create(**project_requirements_data)

            # Process crew requirements
            for crew_item in data.get("crew_requirements", []):
                crew_obj, _ = ProjectCrewRequirement.objects.update_or_create(
                    project=project,
                    crew_title=crew_item.get("title"),
                    defaults={"quantity": crew_item.get("quantity", 1)}
                )
                project_requirements.crew_requirements.add(crew_obj)

            # Process equipment requirements
            for equipment_item in data.get("equipment_requirements", []):
                equipment_obj, _ = ProjectEquipmentRequirement.objects.update_or_create(
                    project=project,
                    equipment_title=equipment_item.get("title"),
                    defaults={"quantity": equipment_item.get("quantity", 1)}
                )
                project_requirements.equipment_requirements.add(equipment_obj)

            # Serialize and return the response
            serializer = self.get_serializer(project_requirements)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        validated_data = request.data
        user = request.user

        # Check permissions
        project = get_object_or_404(ProjectDetails, project_id=validated_data.get("project"))
        if project.owner != user and not Membership.objects.filter(project=project, user=user).exists():
            raise PermissionDenied("You do not have permission to update requirements for this project.")

        # Update main ProjectRequirements fields
        instance.budget_currency = validated_data.get("budget_currency", instance.budget_currency)
        instance.budget = validated_data.get("budget", instance.budget)
        instance.updated_by = user
        instance.save()

        # Update or create crew requirements
        crew_data = validated_data.get("crew_requirements", [])
        instance.crew_requirements.clear()  # Clear existing crew requirements
        for crew_item in crew_data:
            crew_obj, _ = ProjectCrewRequirement.objects.update_or_create(
                project=project,
                crew_title=crew_item.get("title"),
                defaults={"quantity": crew_item.get("quantity", 1)}
            )
            instance.crew_requirements.add(crew_obj)

        # Update or create equipment requirements
        equipment_data = validated_data.get("equipment_requirements", [])
        instance.equipment_requirements.clear()  # Clear existing equipment requirements
        for equipment_item in equipment_data:
            equipment_obj, _ = ProjectEquipmentRequirement.objects.update_or_create(
                project=project,
                equipment_title=equipment_item.get("title"),
                defaults={"quantity": equipment_item.get("quantity", 1)}
            )
            instance.equipment_requirements.add(equipment_obj)

        # Serialize and return the updated instance
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Shooting Details Viewset
class ShootingDetailsViewSet(viewsets.ModelViewSet):
    queryset = ShootingDetails.objects.all()
    serializer_class = ShootingDetailsSerializer
    permission_classes = [IsAuthenticated]


# Role Viewset
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    # Customize role creation for a project
    def create(self, request, *args, **kwargs):
        data = request.data
        if 'project' in data:
            project_id = data['project']
            project = ProjectDetails.objects.get(id=project_id)
            data['project'] = project.id
        return super().create(request, *args, **kwargs)


# Membership Viewset
class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        role_id = data.get('role_id')
        
        try:
            project = ProjectDetails.objects.get(project_id=project_id)
        except ProjectDetails.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        role = Role.objects.get(id=role_id)
        
        # Create a new membership
        membership = Membership.objects.create(user=user_id, role=role, project=project)
        membership.save()

        return Response({'message': 'Membership created successfully'}, status=status.HTTP_201_CREATED)
    
class FirstProjectView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user=request.user
            data=request.data
            project_details = data['project_details']
            print(project_details)
            
            create_project_permission = AccountPermission.objects.get(name='create_project')
            user_type = user.user_type
        
            if user_type is None or not user_type.permissions.filter(id=create_project_permission.id).exists():
                raise PermissionDenied("You don't have permission to create a project.")
        
            project_details['owner'] = user
        
            try:
                project = ProjectDetails.objects.create(**project_details)
                print(project)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            admin_role = Role.objects.filter(name='admin').first()  # Adjust the role name as necessary
        
            if admin_role:
                Membership.objects.create(user=user, role=admin_role, project=project)
            
            project_requirements_data = {
                "project": project,
                "budget_currency": data.get("budget_currency", "$"),
                "budget": data.get("budget"),
                "created_by": user,
                "updated_by": user,
            }
            project_requirements = ProjectRequirements.objects.create(**project_requirements_data)

            # Process crew requirements
            for crew_item in data.get("crew_requirements", []):
                crew_obj, _ = ProjectCrewRequirement.objects.update_or_create(
                    project=project,
                    crew_title=crew_item.get("title"),
                    defaults={"quantity": crew_item.get("quantity", 1)}
                )
                project_requirements.crew_requirements.add(crew_obj)

            # Process equipment requirements
            for equipment_item in data.get("equipment_requirements", []):
                equipment_obj, _ = ProjectEquipmentRequirement.objects.update_or_create(
                    project=project,
                    equipment_title=equipment_item.get("title"),
                    defaults={"quantity": equipment_item.get("quantity", 1)}
                )
                project_requirements.equipment_requirements.add(equipment_obj)

            return Response({
                'success': True,
                'message': 'First project created successfully',
                'data': {
                    'project': ProjectDetailsSerializer(project).data,
                    'project_requirements': ProjectRequirementsSerializer(project_requirements).data
                }
                },status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except KeyError:
            return Response({'error': 'Project details not found in request data'}, status=status.HTTP_400_BAD_REQUEST)

class SuggestionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            project_id = request.data['project_id']
            return Response({
                    'success': True,
                    'message': 'Data',
                    'data': {
                        'project_id': project_id,
                        'suggestion': project_ai_suggestion(project_id)
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)