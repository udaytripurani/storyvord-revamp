from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from project.models import Membership, ProjectDetails
from rest_framework.permissions import IsAuthenticated
from client.models import ClientProfile
from storyvord.exception_handlers import custom_exception_handler

class CalendarView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CalendarSerializer

    def get(self, request, project_id=None):
        try:
            if project_id:
                calendar = get_object_or_404(ProjectCalendar, project=project_id)
                serializer = self.serializer_class(calendar)
            else:
                # RBAC
                calendars = ProjectCalendar.objects.filter(
                    project__memberships__user = request.user
                ).distinct()

                serializer = self.serializer_class(calendars, many=True)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

class EventView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def check_rbac(self, user, project, permission_name):
        membership = get_object_or_404(Membership, user=user, project=project)
        if not membership.role.permission.filter(name=permission_name).exists():
            return False
        return True

    def get(self, request, project_id, pk=None):
        try:
            calendar = get_object_or_404(ProjectCalendar, project=project_id)
            
            # membership = get_object_or_404(Membership, user=request.user, project=calendar.project)
            # print(membership.role.permission.all())
            # if not membership.role.permission.filter(name='view_calander').exists():
                # raise PermissionError('You do not have permission to view this calendar')

            # RBAC
            if not self.check_rbac(request.user, calendar.project, 'view_calander_event'):
                raise PermissionError('You do not have permission to view this calendar')
            
            
            if pk:
                serializer = self.serializer_class(get_object_or_404(CalendarEvent, pk=pk, calendar=calendar))
                
            else:
                serializer = self.serializer_class(calendar.calendar_events.all(), many=True)


            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def post(self, request, project_id):
        try:
            calendar = get_object_or_404(ProjectCalendar, project=project_id)

            # RBAC
            if not self.check_rbac(request.user, calendar.project, 'create_calander_event'):
                raise PermissionError('You do not have permission to create this calendar event')

            # Prepare data for the serializer
            data = request.data.copy()
            data['calendar'] = calendar.id
            data['project'] = project_id

            # Pass data to the serializer
            serializer = self.serializer_class(data=data, context={'request': request})

            # Validate and save the event
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            data['participants'] = [Membership.objects.get(id=participant_id).id for participant_id in data['participants']]

            serializer.save()
            response_data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, project_id, pk):
        try:
            calendar = get_object_or_404(ProjectCalendar, project=project_id)

            # RBAC
            if not self.check_rbac(request.user, calendar.project, 'edit_calander_event'):
                raise PermissionError('You do not have permission to edit this calendar event')

            event = get_object_or_404(CalendarEvent, pk=pk, calendar=calendar)
            data = request.data.copy()
            data['calendar'] = calendar.id
            data['project'] = project_id
            serializer = self.serializer_class(event, data=data, context={'request': data})
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            data['participants'] = [Membership.objects.get(id=participant_id).id for participant_id in data['participants']]

            serializer.save()
            response_data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(response_data)

        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        
    def delete(self, request, project_id, pk):
        try:
            calendar = get_object_or_404(ProjectCalendar, project=project_id)

            # RBAC
            if not self.check_rbac(request.user, calendar.project, 'delete_calander_event'):
                raise PermissionError('You do not have permission to delete this calendar events')
            
            event = get_object_or_404(CalendarEvent, pk=pk, calendar=calendar)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
    
    
class UserCalendarView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCalendarSerializer

    
    def get(self, request):
        try:
            # Get or create user calendar
            user_calendar, _ = UserCalender.objects.get_or_create(user=request.user)
            serializer = self.serializer_class(user_calendar)
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        

        
class UserCalendarEventView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCalendarEventSerializer

    def post(self, request):    
        try:
            user_calendar = get_object_or_404(UserCalender, user=request.user)
            data = request.data.copy()
            data['calendar'] = user_calendar.id
            data['user'] = request.user.id 
            print(data)
            serializer = self.serializer_class(data=data, context={'request': data})
            # serializer.is_valid(exception=True)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response

    def put(self, request, pk):
        try:
            user_calendar = get_object_or_404(UserCalender, user=request.user)
            event = get_object_or_404(UserCalendarEvent, pk=pk, calendar=user_calendar)
            data = request.data.copy()
            data['calendar'] = user_calendar.id 
            serializer = self.serializer_class(event, data=data, context={'request': data})
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            serializer.save()
            data = {
                'message': 'Success',
                'data': serializer.data
            }
            return Response(data)
        except Exception as exc:
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        
    def delete(self, request, pk):
        try:
            user_calendar = get_object_or_404(UserCalender, user=request.user)
            event = get_object_or_404(UserCalendarEvent, pk=pk, calendar=user_calendar)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            print(exc)
            response = custom_exception_handler(exc, self.get_renderer_context())
            return response
        

        

# User Calander View of all events of calander and user calander  
class UserHomeCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch the user's personal calendar and events
            user_calendar = get_object_or_404(UserCalender, user=request.user)
            user_calendar_events = user_calendar.user_calendar_events.all()

            # Fetch all project calendars where the user is part of a membership
            project_calendars = ProjectCalendar.objects.filter(
                project__memberships__user=request.user
            ).distinct()

            # Fetch all events from the project calendars where the user is a participant
            project_calendar_events = CalendarEvent.objects.filter(
                participants__user=request.user
            ).distinct()

            # Serializing user calendar and its events
            user_calendar_serializer = UserCalendarSerializer(user_calendar)
            user_calendar_events_serializer = UserCalendarEventSerializer(user_calendar_events, many=True)

            # Serializing project calendars and their events
            project_calendars_serializer = CalendarSerializer(project_calendars, many=True)
            project_calendar_events_serializer = EventSerializer(project_calendar_events, many=True)

            # Combine all data in the response
            data = {
                'message': 'Success',
                'data': {
                    'user_calendar': {
                        'calendar': user_calendar_serializer.data,
                        'events': user_calendar_events_serializer.data
                    },
                    'project_calendars': {
                        'calendars': project_calendars_serializer.data,
                        'events': project_calendar_events_serializer.data
                    }
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            print(f"Error: {exc}")
            response = custom_exception_handler(exc, self.get_renderer_context())
            return responseesponse