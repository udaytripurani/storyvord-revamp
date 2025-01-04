from django.conf import settings
from django.db import models

from project.models import Project, ProjectDetails, Membership
from accounts.models import User

# Create your models here.

class ProjectCalendar(models.Model):
    project = models.OneToOneField(ProjectDetails, on_delete=models.CASCADE, related_name='project_calendar')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class CalendarEvent(models.Model):
    calendar = models.ForeignKey(ProjectCalendar, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(Membership, related_name='calendar_events', blank=True)

    def __str__(self):
        return self.title
    
class UserCalender(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_calendar')
    name = models.CharField(max_length=255, default='My Calendar')

    def __str__(self):
        return self.name
    
class UserCalendarEvent(models.Model):
    calendar = models.ForeignKey(UserCalender, on_delete=models.CASCADE, related_name='user_calendar_events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    # participants = models.ManyToManyField(User, related_name='user_calendar_events', blank=True)

    def __str__(self):
        return self.title