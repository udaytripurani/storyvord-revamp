from rest_framework import serializers
from django.core.files.base import ContentFile
from .models import *
from client.models import ClientProfile
import base64

class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

class EventSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CalendarEvent
        fields = '__all__'

    def validate_participants(self, value):
        calendar_id = self.initial_data.get('calendar')
        project = self.initial_data.get('project')

        # Check if the provided calendar exists
        try:
            calendar = ProjectCalendar.objects.get(id=calendar_id)
        except ProjectCalendar.DoesNotExist:
            raise serializers.ValidationError("Invalid calendar ID.")

        # Check if all participant IDs are valid Memberships for the project's memberships
        participants = []
        for participant_id in value:
            id = participant_id.id
            try:
                membership = Membership.objects.get(id=id)
            except Membership.DoesNotExist:
                raise serializers.ValidationError(f"Invalid participant ID: {participant_id}")

            if str(membership.project.project_id) != str(project):
                raise serializers.ValidationError(
                    f"Participant {membership.user.email} is not a member of the project."
                )
            participants.append(id)

        print(participants)
        return participants
    
class CalendarSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True, source='calendar_events')

    class Meta:
        model = ProjectCalendar
        fields = ['id', 'name', 'project', 'events']

class ProjectCalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectCalendar
        fields = '__all__'

class UserCalendarEventSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserCalendarEvent
        fields = '__all__'
    
    # def validate_participants(self, value):
    #     calendar_id = self.initial_data.get('calendar')
    #     calendar = UserCalender.objects.get(id=calendar_id)
    #     user = calendar.user

    #     for participant in value:
    #         if participant != user:
    #             raise serializers.ValidationError(
    #                 f"User {participant.email} is not the owner of this calendar."
    #             )
    #     return value
        
class UserCalendarSerializer(serializers.ModelSerializer):
    user_calendar_events = UserCalendarEventSerializer(many=True, read_only=True)

    class Meta:
        model = UserCalender
        fields = '__all__'