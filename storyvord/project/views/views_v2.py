from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.db.models import Q
from accounts.models import Permission as AccountPermission, PersonalInfo
from client.models import ClientProfile
from crew.models import CrewProfile
from ..models import (
    ProjectDetails, ProjectRequirements, ShootingDetails, ProjectInvite,
    Role, Membership, User, Permission,ProjectCrewRequirement, ProjectEquipmentRequirement,ProjectAISuggestions
)
from decimal import Decimal , InvalidOperation
from ..serializers.serializers_v2 import (
    ProjectDetailsSerializer, ProjectInviteSerializer, ProjectRequirementsSerializer, ShootingDetailsSerializer, 
    RoleSerializer, MembershipSerializer,ProjectAISuggestionsSerializer, PersonalInfoSerializer , CrewProfileSerializer, ClientProfileSerializer
)
import uuid
from django.http import JsonResponse
from project.utils import generate_report, generate_report_v2, project_ai_suggestion

import logging
logger = logging.getLogger(__name__)

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
        try:
            return ProjectDetails.objects.filter(
                Q(owner=self.request.user) | 
                Q(memberships__user=self.request.user)
            ).order_by('-created_at').distinct()
        except Exception as e:
            logger.error(f"Error occurred while fetching projects for user {self.request.user}. Error: {e}")
            raise e

    def get_object(self):
        """
        Override get_object to provide a more specific error when a project is not found or the user doesn't have access.
        """
        return ProjectDetails.objects.filter(
            Q(owner=self.request.user) | 
            Q(memberships__user=self.request.user)
        ).distinct().get(pk=self.kwargs['pk'])
    
    # Create a custom action for creating a project-specific role
    #TODO need to add permission check here ->
    @action(detail=True, methods=['post'])
    def create_role(self, request, pk=None):
        project = self.get_object()
        data = request.data
        data['project'] = project.project_id  # Assign the project to the role
        role_serializer = RoleSerializer(data=data)
        if role_serializer.is_valid():
            role_serializer.save()
            logger.info(f"User {self.request.user.id} created role {role_serializer.data['name']} in project {project.project_id}")
            return Response(role_serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"User {self.request.user.id} tried to create role in project {project.project_id} with invalid data")
        return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Action to manage adding/removing members from a project
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        try:
            project = self.get_object()
            logger.info(f"User {self.request.user.id} trying to add member to project {project}")
            
            user = request.data.get('user_id')
            role = request.data.get('role_id')
            
            if not user or not role:
                logger.warning(f"User {self.request.user.id} tried to add member to project {project} with invalid data")
                return Response({'error': 'User and Role are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Membership.objects.filter(project=project, user_id=user).exists():
                    logger.warning(f"User {self.request.user.id} tried to add member {user} to project {project} which is already a member")
                    return Response({'error': 'User is already a member of the project'}, status=status.HTTP_400_BAD_REQUEST)
                
            if request.user == project.owner or Membership.objects.filter(
                project=project, 
                user=request.user,
                role__permission__name='add_members'
            ).exists():
                invitee = get_object_or_404(User, id=user)
                role = get_object_or_404(Role, id=role)
                
                invite, created = ProjectInvite.objects.get_or_create(
                    project=project,
                    inviter=request.user,
                    invitee=invitee,
                    role=role,
                )
                if created:
                    logger.info(f"User {request.user.id} successfully invited member {user} to project {project}")
                    return Response(
                        {
                            'message': 'Invitation sent successfully',
                            'data': model_to_dict(invite)
                        }, status=status.HTTP_201_CREATED)
                else:
                    logger.info(f"User {request.user.id} tried to re-invite member {user} to project {project} who already has a pending invite")
                    return Response(
                        {
                            'message': 'Invitation already exists',
                            'data': {
                                'invite_id': invite.id,
                                'inviter': invite.inviter.id,
                                'invitee': invite.invitee.id,
                                'role': invite.role.id
                                }
                        }, status=status.HTTP_200_OK)
                
            else:
                logger.warning(f"User {self.request.user.id} tried to add member {user} to project {project} which they do not have permission for")
                raise PermissionDenied("You don't have permission to add members to this project.")
            
        except ProjectDetails.DoesNotExist:
            logger.warning(f"User {request.user.id} tried to access project {pk} which does not exist or they have no access")
            return Response({'error': 'Project does not exist or you do not have access to it.'}, status=status.HTTP_404_NOT_FOUND)

        except PermissionDenied as e:
            logger.warning(f"User {request.user.id} tried to invite member to project {project} without permission")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Unexpected error occurred while {request.user.id} tried to invite member to project {project}. Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class RespondToInviteView(APIView):
    """
    Handle user responses to project invitations.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id):
        try:
            # Retrieve the invite, ensuring the invitee is the requesting user
            try:
                invite = ProjectInvite.objects.get(id=invite_id, invitee=request.user)
            except ProjectInvite.DoesNotExist:
                return Response({'error': 'Invitation not found or you do not have permission to respond.'}, status=404)

            # Validate the action
            action = request.data.get('action')  # "accept" or "reject"
            if action not in ['accept', 'reject']:
                raise ValidationError({'error': 'Invalid action. Must be "accept" or "reject".'})

            # Process the action
            if action == 'accept':
                invite.accept()
                return Response({'message': 'Invite accepted'}, status=200)
            elif action == 'reject':
                invite.reject()
                return Response({'message': 'Invite rejected'}, status=200)
        
        except Exception as e:
            logger.error(f"Unexpected error occurred while {request.user.id} tried to respond to invite {invite_id}. Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetInvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch invites for the authenticated user
            invites = ProjectInvite.objects.filter(
                Q(inviter=request.user) | Q(invitee=request.user)
            )

            # Serialize the invites
            serializer = ProjectInviteSerializer(invites, many=True)
            invitee_invites = [invite for invite in serializer.data if invite['invitee'] == request.user.id]
            inviter_invites = [invite for invite in serializer.data if invite['inviter'] == request.user.id]

            project_id = request.query_params.get('project_id')
            project_data = {}

            # If project_id is passed, filter the invites by project
            if project_id:
                for invite in invitee_invites + inviter_invites:
                    proj_id = project_id
                    if proj_id not in project_data:
                        project = ProjectDetails.objects.get(Q(project_id=proj_id) & Q(owner=request.user))
                        project_data[proj_id] = {
                            'project_id': project.project_id,
                            'project_name': project.name,
                            'project_status': project.status,
                            'created_at': project.created_at,
                            'invites': []
                        }
                    project_data[proj_id]['invites'].append({
                        'invite_id': invite['id'],
                        'invitee_or_inviter': 'invitee' if invite['invitee'] == request.user.id else 'inviter',
                        'status': invite['status'],
                        'updated_at': invite['updated_at']
                    })

            # If project_id is not passed, return all invites
            else:
                for invite in invitee_invites + inviter_invites:
                    proj_id = invite['project']
                    if proj_id not in project_data:
                        project = ProjectDetails.objects.get(project_id=proj_id)
                        project_data[proj_id] = {
                            'project_id': project.project_id,
                            'project_name': project.name,
                            'project_status': project.status,
                            'created_at': project.created_at,
                            'invites': []
                        }
                    project_data[proj_id]['invites'].append({
                        'invite_id': invite['id'],
                        'invitee_or_inviter': 'invitee' if invite['invitee'] == request.user.id else 'inviter',
                        'status': invite['status'],
                        'updated_at': invite['updated_at']
                    })

            response_data = list(project_data.values())
            return Response({
                'status': 'success',
                'message': 'Invites retrieved successfully',
                'data': response_data
            }, status=status.HTTP_200_OK)

        except ProjectDetails.DoesNotExist:
            return Response({'status':'false','message': 'Project does not exist or you do not have permission to view it','data':[]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error occurred while {request.user.id} tried to get invites. Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Project Requirements Viewset
class ProjectRequirementsViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequirements.objects.all()
    serializer_class = ProjectRequirementsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProjectRequirements.objects.filter(
            project=self.request.query_params.get('project_id')
        )
        
    # def list(self, request, *args, **kwargs):
    #     if self.request.query_params.get('project_id') is None:
    #         return Response({'error': 'project_id is required in params'}, status=status.HTTP_400_BAD_REQUEST)
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response({'status': 'success','message': 'Project requirements retrieved successfully' ,'data': serializer.data}, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            req_id = kwargs['pk']
            req = get_object_or_404(ProjectRequirements, id=req_id)
            if req.project.owner != request.user and not Membership.objects.filter(project=req.project, user=request.user).exists():  #TODO Add role based permission instead of user.
                raise PermissionDenied("You do not have permission to view this project requirements.")
            data = self.get_serializer(req).data
            return Response({'status': 'success','message': 'Project requirements retrieved successfully', 'data': data}, status=status.HTTP_200_OK)
        except ProjectRequirements.DoesNotExist:
            return Response({'error': 'Project requirements not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error occurred while {request.user.id} tried to retrieve project requirements. Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        project = get_object_or_404(ProjectDetails, project_id=data.get("project"))

        # Permission check
        if project.owner != user and not Membership.objects.filter(project=project, user=user).exists():
            logger.warning(f"User {user} tried to create requirements for project {project} without permission")
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
            logger.info(f"Project requirements created for project {project} by user {user}")

            # Process crew requirements
            for crew_item in data.get("crew_requirements", []):
                crew_obj, _ = ProjectCrewRequirement.objects.update_or_create(
                    project=project,
                    crew_title=crew_item.get("title"),
                    defaults={"quantity": crew_item.get("quantity", 1)}
                )
                project_requirements.crew_requirements.add(crew_obj)
                logger.info(f"Crew requirement added: {crew_item.get('title')} for project {project}")

            # Process equipment requirements
            for equipment_item in data.get("equipment_requirements", []):
                equipment_obj, _ = ProjectEquipmentRequirement.objects.update_or_create(
                    project=project,
                    equipment_title=equipment_item.get("title"),
                    defaults={"quantity": equipment_item.get("quantity", 1)}
                )
                project_requirements.equipment_requirements.add(equipment_obj)
                logger.info(f"Equipment requirement added: {equipment_item.get('title')} for project {project}")

            # Serialize and return the response
            serializer = self.get_serializer(project_requirements)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating project requirements for project {project} by user {user}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = ProjectRequirements.objects.get(pk=kwargs['pk'])
        validated_data = request.data
        user = request.user

        # Check permissions
        try:
            project = get_object_or_404(ProjectDetails, project_id=validated_data.get("project"))
        except Exception as exc:
            return Response({'status': 'false','message':'Please send the project id in the body of the request', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        #TODO Remove the project id from the request data, it can be retrieved from the requirement instance object

        if project.owner != user and not Membership.objects.filter(project=project, user=user).exists():
            logger.warning(f"User {user.id} tried to update requirements for project {project.project_id} without permission")
            raise PermissionDenied("You do not have permission to update requirements for this project.")

        # Update main ProjectRequirements fields
        try:
            instance.budget_currency = validated_data.get("budget_currency", instance.budget_currency)
            instance.budget = validated_data.get("budget", instance.budget)
            instance.updated_by = user
            instance.save()
            logger.info(f"Project requirements updated for project {project.project_id} by user {user.id}")
        except Exception as e:
            logger.error(f"Error updating project requirements for project {project.project_id} by user {user.id}: {str(e)}")

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
            logger.info(f"Crew requirement updated: {crew_item.get('title')} for project {project.project_id}")

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
            logger.info(f"Equipment requirement updated: {equipment_item.get('title')} for project {project.project_id}")

        # Serialize and return the updated instance
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Shooting Details Viewset
#TODO : Complete shoot details
class ShootingDetailsViewSet(viewsets.ModelViewSet):
    queryset = ShootingDetails.objects.all()
    serializer_class = ShootingDetailsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Only return shooting details of a project if the user has access.
        """
        project_id = self.request.query_params.get('project_id')
        user = self.request.user
        if not project_id:
            logger.warning(f"User {user.id} attempted to access shooting details without a project_id.")
            raise ValidationError({"error": "project_id is required."})

        # Validate UUID format
        try:
            project_id = uuid.UUID(project_id)
        except ValueError:
            logger.error(f"User {user.id} provided an invalid project_id format: {project_id}.")
            raise ValidationError({"error": "Invalid project_id format. Must be a valid UUID."})

        # Check if the project exists
        try:
            project = ProjectDetails.objects.get(project_id=project_id)
            logger.info(f"User {user.id} accessed project {project_id}.")
        except ProjectDetails.DoesNotExist:
            logger.error(f"User {user.id} attempted to access a non-existent project: {project_id}.")
            raise NotFound({"error": "Project not found."})
        
        if project.owner != user and not Membership.objects.filter(project=project, user=user).exists():
            logger.warning(f"User {user.id} does not have permission to access project {project_id}.")
            raise PermissionDenied("You do not have permission to access this project.")

        # Return the filtered queryset
        logger.info(f"User {user.id} accessed shooting details for project {project_id}.")
        return ShootingDetails.objects.filter(project=project).distinct()
    
    def update(self, request, *args, **kwargs):
        try:
            shoot_details = get_object_or_404(ShootingDetails,id=kwargs['pk'])
            validated_data = request.data
            if shoot_details.project.owner != request.user and not Membership.objects.filter(project=shoot_details.project, user=request.user).exists():
                logger.warning(f"User {request.user.id} tried to update requirements for project {shoot_details.project.project_id} without permission")
                raise PermissionDenied("You do not have permission to update requirements for this project.")

            serializer = self.get_serializer(shoot_details, data=validated_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Shooting details updated for project {shoot_details.project.project_id} by user {request.user.id}")
            return Response({'status': 'success','message': 'Shooting details updated successfully','data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            
    
    def retrieve(self, request, *args, **kwargs):
        try:
            shoot_details = get_object_or_404(ShootingDetails, id=kwargs['pk'])
            if shoot_details.project.owner != request.user and not Membership.objects.filter(project=shoot_details.project, user=request.user).exists():  #TODO Add role based permission instead of user.
                raise PermissionDenied("You do not have permission to view this shoot details")
            data = self.get_serializer(shoot_details).data
            return Response({'status': 'success','message': 'Shooting details retrieved successfully','data':data}, status=status.HTTP_200_OK)
        except ShootingDetails.DoesNotExist:
            return Response({'error': 'Shoot Details not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error occurred while {request.user.id} tried to retrieve shoot details. Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            data['project'] = project.project_id
        return super().create(request, *args, **kwargs)


# Membership Viewset
class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            return Membership.objects.filter(
                Q(project=self.request.query_params.get('project_id'))&
                Q(project__owner=self.request.user)&
                Q(project__memberships__user=self.request.user)
            ).distinct()
        except Exception as e:
            logger.error(f"Error occurred while fetching memberships for user {self.request.user}. Error: {e}")
            raise e
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = []

            for membership in queryset:
                membership_data = {
                    "membership_id": membership.id,
                    "project_id": membership.project.project_id if membership.project else None,
                    "created_at": membership.created_at,
                    "user": {}
                }

                # User details
                user = membership.user
                membership_data["user"]["id"] = user.id
                membership_data["user"]["email"] = user.email

                # Personal Info
                try:
                    personal_info = PersonalInfo.objects.get(user=user)
                    membership_data["user"]["personal_info"] = {
                        "full_name": personal_info.full_name,
                        "contact_number": personal_info.contact_number,
                        "location": personal_info.location,
                        "languages": personal_info.languages,
                        "job_title": personal_info.job_title,
                        "bio": personal_info.bio,
                        "image": personal_info.image.url if personal_info.image and personal_info.image.name else None,
                    }
                except PersonalInfo.DoesNotExist:
                    membership_data["user"]["personal_info"] = None

                # Client Profile
                if user.user_type_id == 1:
                    try:
                        client_profile = ClientProfile.objects.get(user=user)
                        membership_data["user"]["client_profile"] = {
                            "role": client_profile.role,
                            "address": client_profile.address,
                            "personal_website": client_profile.personalWebsite,
                            "drive": client_profile.drive,
                            "active": client_profile.active,
                        }
                    except ClientProfile.DoesNotExist:
                        membership_data["user"]["client_profile"] = None

                # Crew Profile
                elif user.user_type_id == 2:
                    try:
                        crew_profile = CrewProfile.objects.get(user=user)
                        membership_data["user"]["crew_profile"] = {
                            "experience": crew_profile.experience,
                            "skills": crew_profile.skills,
                            "standard_rate": crew_profile.standardRate,
                            "technical_proficiencies": crew_profile.technicalProficiencies,
                            "specializations": crew_profile.specializations,
                            "drive": crew_profile.drive,
                            "active": crew_profile.active,
                        }
                    except CrewProfile.DoesNotExist:
                        membership_data["user"]["crew_profile"] = None

                # Role Information
                if membership.role:
                    membership_data["role"] = {
                        "name": membership.role.name,
                        "description": membership.role.description,
                        "is_global": membership.role.is_global,
                        "permissions": [permission.name for permission in membership.role.permission.all()]
                    }
                else:
                    membership_data["role"] = None

                # Append the membership data to the final list
                serialized_data.append(membership_data)

        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "status": "success",
                "message": "Memberships retrieved successfully",
                "data": serialized_data,
            },
            status=status.HTTP_200_OK,
        )
    
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
            logger.info(f"First project creation request from user {request.user.id}: {request.data}")
            user = request.user
            data = request.data
            
            if 'project_details' not in data:
                raise KeyError("Project details not found in request data")
            
            project_serializer = ProjectDetailsSerializer(data=data['project_details'], context={'request': request})
            project_serializer.is_valid(raise_exception=True)
            project = project_serializer.save(owner=user)
            logger.info(f"Project created: {project}")
            
            project_requirements = data.get('project_requirement')
            logger.info(f"Project requirements: {project_requirements}")
            project_requirements_data = {
                "project": project,
                "budget_currency": project_requirements.get("budget_currency"),
                "budget": project_requirements.get("budget"),
                "created_by": user,
                "updated_by": user,
            }
            project_requirements = ProjectRequirements.objects.create(**project_requirements_data)
            logger.info(f"Project requirements created: {project_requirements}")
            
            shoot_details = []
            for shooting_detail in data.get("shooting_details", []):
                shooting_details_data = {
                    "project": project,
                    "location": shooting_detail.get("location"),
                    "start_date": shooting_detail.get("start_date"),
                    "end_date": shooting_detail.get("end_date"),
                    "mode_of_shooting": shooting_detail.get("mode_of_shooting"),
                    "permits": shooting_detail.get("permits"),
                    "created_by": user,
                    "updated_by": user,
                }
                shooting_details = ShootingDetails.objects.create(**shooting_details_data)  
                shoot_details.append(ShootingDetailsSerializer(shooting_details).data)
                logger.info(f"Shooting details created: {shooting_details}")

            # Process crew requirements
            for crew_item in data.get("project_requirement", {}).get("crew_requirements", []):
                crew_obj, _ = ProjectCrewRequirement.objects.update_or_create(
                    project=project,
                    crew_title=crew_item.get("title"),
                    defaults={"quantity": crew_item.get("quantity", 1)}
                )
                project_requirements.crew_requirements.add(crew_obj)
                logger.info(f"Crew requirement created: {crew_obj}")

            # Process equipment requirements
            for equipment_item in data.get("project_requirement", {}).get("equipment_requirements", []):
                equipment_obj, _ = ProjectEquipmentRequirement.objects.update_or_create(
                    project=project,
                    equipment_title=equipment_item.get("title"),
                    defaults={"quantity": equipment_item.get("quantity", 1)}
                )
                project_requirements.equipment_requirements.add(equipment_obj)
                logger.info(f"Equipment requirement created: {equipment_obj}")
                
            user.steps = True
            user.save()

            return Response({
                'success': True,
                'message': 'First project created successfully',
                'data': {
                    'project': ProjectDetailsSerializer(project).data,
                    'project_requirements': ProjectRequirementsSerializer(project_requirements).data,
                    'shooting_details': shoot_details
                }
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            logger.error(f"Key error while creating first project: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception while creating first project: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class SkipOnboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            user.steps = True
            user.save()
            return Response({'message': 'First project skipped successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id, user):
        """
        Retrieve the project and validate user access.
        """
        project = get_object_or_404(ProjectDetails, project_id=project_id)

        if project.owner != user and not Membership.objects.filter(project=project, user=user).exists():
            raise PermissionDenied("You do not have permission to view AI suggestions for this project.")

        return project

    def regenerate_report(self, project, project_details, shooting_details, regenerate=None):
        """
        Generate or regenerate specific reports based on the regenerate parameter.
        """
        reports = {}
        if not regenerate or "logistics" in regenerate:
            reports["logistics"] = generate_report("logistics", project_details, shooting_details)
        if not regenerate or "budget" in regenerate:
            reports["budget"] = generate_report("budget", project_details, shooting_details)
        if not regenerate or "compliance" in regenerate:
            reports["compliance"] = generate_report("compliance", project_details, shooting_details)
        if not regenerate or "culture" in regenerate:
            reports["culture"] = generate_report("culture", project_details, shooting_details)

        # Update or create AI suggestions in the database
        ProjectAISuggestions.objects.update_or_create(
            project=project,
            defaults={
                'suggested_logistics': reports.get("logistics", ""),
                'suggested_budget': reports.get("budget", ""),
                'suggested_compliance': reports.get("compliance", ""),
                'suggested_culture': reports.get("culture", "")
            }
        )
        return reports
    
    def renerate_report_v2(self, project, project_details, shooting_details, regenerate=None):
        reports = {}
        if not regenerate or "logistics" in regenerate:
            reports["logistics"] = generate_report_v2("logistics", project_details, shooting_details)
        if not regenerate or "budget" in regenerate:
            reports["budget"] = generate_report_v2("budget", project_details, shooting_details)
        if not regenerate or "compliance" in regenerate:
            reports["compliance"] = generate_report_v2("compliance", project_details, shooting_details)
        if not regenerate or "culture" in regenerate:
            reports["culture"] = generate_report_v2("culture", project_details, shooting_details)

        # Update or create AI suggestions in the database
        ProjectAISuggestions.objects.update_or_create(
            project=project,
            defaults={
                'suggested_logistics': reports.get("logistics", ""),
                'suggested_budget': reports.get("budget", ""),
                'suggested_compliance': reports.get("compliance", ""),
                'suggested_culture': reports.get("culture", "")
            }
        )
        return reports

    def get(self, request):
        try:
            project_id = request.query_params.get('project_id')
            regenerate = request.query_params.getlist('regenerate')

            if not project_id:
                return Response({'error': 'project_id is required.'}, status=400)

            project = self.get_project(project_id, request.user)

            # Fetch related data
            requirements = ProjectRequirements.objects.get(project=project)
            shooting_details = ShootingDetails.objects.filter(project=project).values()
            project_details = project.brief

            # Fetch cached suggestions if no regeneration is requested
            if not regenerate:
                cached_suggestions = ProjectAISuggestions.objects.filter(project=project).first()
                if cached_suggestions:
                    serialized_suggestions = {
                        'logistics': cached_suggestions.suggested_logistics,
                        'budget': cached_suggestions.suggested_budget,
                        'compliance': cached_suggestions.suggested_compliance,
                        'culture': cached_suggestions.suggested_culture,
                    }
                    return Response({
                        'success': True,
                        'message': 'Cached data retrieved.',
                        'data': {
                            'project_id': project_id,
                            'suggestion': "Suggestions already available in the database.",
                            'report': serialized_suggestions
                        }
                    }, status=200)

            # Generate AI suggestion
            ai_suggestion = project_ai_suggestion(project, requirements, shooting_details)

            # Regenerate specific reports or all reports
            reports = self.regenerate_report(project, project_details, shooting_details, regenerate)
            
            # reports_v2 = self.renerate_report_v2(project, project_details, shooting_details, regenerate)

            return Response({
                'success': True,
                'message': 'Data generated successfully.',
                'data': {
                    'project_id': project_id,
                    'suggestion': ai_suggestion,
                    'report': reports
                    # 'reports_v2': reports_v2
                }
            }, status=200)

        except ProjectRequirements.DoesNotExist:
            return Response({'error': 'Project requirements not found.'}, status=404)
        except Exception as e:
            logger.error(f"Error in SuggestionView: {str(e)}")
            return Response({'error': str(e)}, status=500)
