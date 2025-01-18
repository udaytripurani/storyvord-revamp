# views.py
import uuid
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from notification.models import Notification
from .models import Announcement
from .serializers import *
from accounts.models import User
from project.models import Membership, Project
from client.models import ClientProfile
from storyvord.exception_handlers import custom_exception_handler
from project.models import ProjectDetails
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

class AnnouncementListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementSerializer

    def get(self, request):
        try:
            announcements = Announcement.objects.all()
            serializer = AnnouncementSerializer(announcements, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request):
        try:
            serializer = AnnouncementSerializer(data=request.data)
            serializer.is_valid(exception=True)
            announcement = serializer.save()
            # Create notifications for recipients
            for user in announcement.recipients.all():
                Notification.objects.create(user=user, announcement=announcement, details="Notification from Announcement")
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
import logging
logger = logging.getLogger(__name__)

# Configure logging
logger = logging.getLogger(__name__)

class AnnouncementRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementSerializer

    def get_object(self, project_id):
        logger.debug(f"Fetching Announcement object with project_id: {project_id}")
        try:
            # Modify to fetch Announcement based on project_id from query params
            announcement = get_object_or_404(Announcement, project_id=project_id)
            self.check_object_permissions(self.request, announcement)
            return announcement
        except Exception as exc:
            logger.error(f"Error fetching Announcement object: {exc}")
            raise

    def get(self, request):
        # Access project_id from query params
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'message': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"GET request received for project_id: {project_id}")
        try:
            announcement = self.get_object(project_id)
            serializer = AnnouncementSerializer(announcement)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            logger.info(f"GET request successful for project_id: {project_id}")
            return Response(data)
        except Exception as exc:
            logger.error(f"Error during GET request for project_id: {project_id}: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request):
        # Access project_id from query params
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'message': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"PUT request received for project_id: {project_id} with data: {request.data}")
        try:
            # Fetch the Announcement object based on project_id
            announcement = self.get_object(project_id)
            serializer = AnnouncementSerializer(announcement, data=request.data)
            serializer.is_valid(raise_exception=True)
            announcement = serializer.save()
            logger.info(f"Announcement with project_id: {project_id} updated successfully.")

            # Create notifications for recipients
            for user in announcement.recipients.all():
                Notification.objects.create(user=user, announcement=announcement, details="Notification from Announcement")
                logger.debug(f"Notification created for user: {user.id}")

            return Response(serializer.data)
        except Exception as exc:
            logger.error(f"Error during PUT request for project_id: {project_id}: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request):
        # Access project_id from query params
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'message': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"DELETE request received for project_id: {project_id}")
        try:
            announcement = self.get_object(project_id)
            announcement.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            logger.info(f"Announcement with project_id: {project_id} deleted successfully.")
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            logger.error(f"Error during DELETE request for project_id: {project_id}: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response


    
class RecipientAnnouncementListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementSerializer

    def get(self, request):
        try:
            # Get announcements where the authenticated user is a recipient
            announcements = Announcement.objects.filter(recipients=request.user)
            serializer = AnnouncementSerializer(announcements, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class RecipientAnnouncementDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementSerializer
    def get_object(self, pk):
        # Get announcement where the authenticated user is a recipient
        announcement = get_object_or_404(Announcement, pk=pk, recipients=self.request.user)
        return announcement

    def get(self, request, pk):
        try:
            announcement = self.get_object(pk)
            serializer = AnnouncementSerializer(announcement)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
class ProjectUserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try: 
            project = get_object_or_404(Project, pk=project_id)

            all_users_data = []
            all_users_data.extend([{"user": user, "source": "crew"} for user in project.crew_profiles.all()])
            all_users_data.append({"user": project.user, "source": "owner"})
            client_profile = ClientProfile.objects.filter(user=project.user).first()
            if client_profile:
                all_users_data.extend([{"user": user, "source": "employee"} for user in client_profile.employee_profile.all()])

            serializer = UserWithSourceSerializer(all_users_data, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from django.db.models import Q
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from django.db.models import Q
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class ProjectAnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing project announcements.
    Handles CRUD operations with proper authorization checks.
    """
    queryset = ProjectAnnouncement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectAnnouncementSerializer

    def get_queryset(self):
        """
        Returns queryset filtered by project_id and user authorization.
        """
        project_id = self.request.data.get("project_id") or self.request.query_params.get("project_id")
        if not project_id:
            return ProjectAnnouncement.objects.none()
        
        try:
            project_id = UUID(project_id)
        except ValueError:
            logger.error(f"Invalid project_id value: {project_id}")
            return ProjectAnnouncement.objects.none()
        
        user = self.request.user
        is_authorized = ProjectDetails.objects.filter(
            project_id=project_id
        ).filter(
            Q(owner=user) | Q(memberships__user=user)
        ).exists()

        if is_authorized:
            return ProjectAnnouncement.objects.filter(project_id=project_id).distinct()

        logger.warning(f"Unauthorized access attempt by user {user.id} for project_id {project_id}")
        return ProjectAnnouncement.objects.none()

    def get_object(self):
        """
        Returns the announcement object if user has permission.
        """
        try:
            user = self.request.user
            announcement = ProjectAnnouncement.objects.get(pk=self.kwargs['pk'])
            project_id = announcement.project.project_id
            
            # Check user membership
            membership = Membership.objects.filter(
                project_id=project_id, user=user
            ).first()
            
            if not membership:
                logger.warning(f"User {user.id} not a member of project {project_id}")
                return None
                
            if not announcement.recipients.filter(id=membership.id).exists():
                logger.warning(f"User {user.id} does not have access to this announcement")
                return None
                
            return announcement
        except ProjectAnnouncement.DoesNotExist:
            logger.error(f"Announcement with pk={self.kwargs['pk']} not found")
            raise Http404
        except Exception as exc:
            logger.error(f"Error retrieving announcement with pk={self.kwargs['pk']}: {str(exc)}")
            raise exc

    def create(self, request, *args, **kwargs):
        """
        Create a new announcement.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(
                    {'message': 'Validation error', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            announcement = serializer.save()
            logger.info(f"Announcement {announcement.id} created successfully")
            
            return Response({
                'message': 'Announcement created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating announcement: {str(e)}")
            return Response(
                {'message': 'An error occurred while creating the announcement'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single announcement.
        """
        try:
            announcement = self.get_object()
            if not announcement:
                return Response(
                    {
                        'message': 'You do not have permission to view this announcement',
                        'data': None
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            data = {
                'message': 'Success',
                'data': {
                    'id': announcement.id,
                    'project_id': str(announcement.project.project_id),
                    'title': announcement.title,
                    'description': announcement.message,
                    'is_urgent': announcement.is_urgent,
                    'recipients': [
                        {
                            'user_id': membership.user.id,
                            'membership_id': membership.id,
                            'email': membership.user.email
                        } for membership in announcement.recipients.all()
                    ],
                }
            }
            return Response(data)
            
        except Http404:
            return Response(
                {'message': 'Announcement not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            logger.error(f"Error retrieving announcement: {str(exc)}")
            return Response(
                {'message': 'An error occurred while retrieving the announcement'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """
        Update an announcement (PUT/PATCH).
        """
        try:
            logger.info(f"Attempting to update announcement with pk={self.kwargs['pk']}")
            instance = self.get_object()
            if not instance:
                return Response(
                    {'message': 'Announcement not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Determine if this is a PATCH or PUT request
            partial = kwargs.pop('partial', False)
            
            # Clone request.data to make it mutable
            data = request.data.copy()
            
            # For PUT requests, ensure project field is included
            if not partial and 'project' not in data:
                data['project'] = str(instance.project.project_id)

            serializer = self.get_serializer(
                instance,
                data=data,
                partial=partial
            )

            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(
                    {'message': 'Validation error', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            announcement = serializer.save()
            
            response_data = {
                'message': 'Announcement updated successfully',
                'data': serializer.data
            }
            
            logger.info(f"Announcement {announcement.id} updated successfully")
            return Response(response_data, status=status.HTTP_200_OK)

        except Http404:
            logger.error("Announcement not found")
            return Response(
                {'message': 'Announcement not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            logger.error(f"Permission denied: {str(e)}")
            return Response(
                {'message': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Unexpected error during update: {str(e)}")
            return Response(
                {'message': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """
        Delete an announcement.
        """
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {'message': 'Announcement not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )

            self.perform_destroy(instance)
            logger.info(f"Announcement {kwargs['pk']} deleted successfully")
            return Response(
                {'message': 'Announcement deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Http404:
            logger.error("Announcement not found")
            return Response(
                {'message': 'Announcement not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            logger.error(f"Permission denied: {str(e)}")
            return Response(
                {'message': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Unexpected error during deletion: {str(e)}")
            return Response(
                {'message': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )








    # def post(self, request, project_id):
    #     try:
    #         project = get_object_or_404(ProjectDetails, pk=project_id)
    #         serializer = ProjectAnnouncementSerializer(data=request.data)
    #         serializer.is_valid(exception=True)
    #         announcement = serializer.save(project=project)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     except Exception as exc:
    #         response = custom_exception_handler(exc, self.get_renderer_context())
    #         return response