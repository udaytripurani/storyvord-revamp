# views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from notification.models import Notification
from .models import Announcement
from .serializers import *
from accounts.models import User
from project.models import Project
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
    
class AnnouncementRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementSerializer

    def get_object(self, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        self.check_object_permissions(self.request, announcement)
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

    def put(self, request, pk):
        try:
            announcement = self.get_object(pk)
            serializer = AnnouncementSerializer(announcement, data=request.data)
            serializer.is_valid(exception=True)
            announcement = serializer.save()
            # Create notifications for recipients
            for user in announcement.recipients.all():
                Notification.objects.create(user=user, announcement=announcement, details="Notification from Announcement")
            return Response(serializer.data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def delete(self, request, pk):
        try:
            announcement = self.get_object(pk)
            announcement.delete()
            data = {
                'message': 'Success',
                'data': None
            }
            return Response(data ,status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
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
        
class ProjectAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = ProjectAnnouncement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectAnnouncementSerializer

    def get_queryset(self):
        project_id = self.request.data.get("project_id") or self.request.query_params.get("project_id")
        if not project_id:
            return ProjectAnnouncement.objects.none()
            
        user = self.request.user
        is_authorized = ProjectDetails.objects.filter(
            project_id=project_id
        ).filter(
            Q(owner=user) | Q(memberships__user=user)
        ).exists()

        # If authorized, return the ProjectAnnouncement queryset
        if is_authorized:
            return ProjectAnnouncement.objects.filter(project_id=project_id).distinct()
        
        # Return an empty queryset if the user is not authorized
        return ProjectAnnouncement.objects.none()

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