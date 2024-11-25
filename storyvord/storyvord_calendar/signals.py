from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import UserCalender, ProjectCalendar
from project.models import ProjectDetails, Project


def create_user_calendar(sender, instance, created, **kwargs):
    if created:
        # Use get_or_create to avoid duplicate key violations
        UserCalender.objects.get_or_create(user=instance, defaults={'name': 'My Calendar'})
    
@receiver(post_save, sender=ProjectDetails)
def create_project_calendar(sender, instance, created, **kwargs):
    if created:
            ProjectCalendar.objects.create(project=instance)

# @receiver(post_save, sender=Project)
# def create_project_calendar(sender, instance, created, **kwargs):
#     if created:
#         ProjectCalendar.objects.create(project=instance)