from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.conf import settings

from .models import CrewProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CrewProfile.objects.create(user=instance)
    