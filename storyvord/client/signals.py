# client/signals.py
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.conf import settings

from project.models import Project
from storyvord_calendar.models import CalendarEvent, ProjectCalendar, UserCalender, UserCalendarEvent
from .models import ClientProfile, ClientCompanyProfile, ClientCompanyCalendar, Role, Membership
# from crew.models import CrewEvent, CrewProfile, CrewCalendar
from crew.models import CrewProfile
from accounts.models import User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ClientProfile.objects.create(user=instance)
        # CrewProfile.objects.create(user=instance)
        UserCalender.objects.create(user=instance, name=f"{instance.email} User Calendar")
        ClientCompanyProfile.objects.create(user=instance)

# @receiver(post_save, sender=Project)
# def create_calendar(sender, instance, created, **kwargs):
#     if created:
#         ProjectCalendar.objects.create(project=instance, name=f"{instance.name} Calendar")
        
@receiver(post_save, sender=ClientCompanyProfile)
def create_calendar(sender, instance, created, **kwargs):
    if created:
        ClientCompanyCalendar.objects.create(company=instance, name=f"{instance} Calendar")
        
@receiver(m2m_changed, sender=CalendarEvent.participants.through)
def create_crew_event(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            if user.user_type == '2':
                crew_event = UserCalendarEvent(
                    event=instance,
                    crew_member=user,
                    title=instance.title,
                    description=instance.description,
                    start=instance.start,
                    end=instance.end,
                    location=instance.location
                )
                crew_event.clean()
                crew_event.save()

                
@receiver(m2m_changed, sender=ClientCompanyProfile.employee_profile.through)
def create_membership_for_new_employee(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        default_role, created = Role.objects.get_or_create(name='employee')
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            Membership.objects.get_or_create(user=user, role=default_role, company=instance)