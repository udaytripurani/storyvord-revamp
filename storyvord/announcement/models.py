from django.db import models
import logging
from accounts.models import User
from project.models import ProjectDetails, Membership
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)

# Create your models here.
#TODO Check if we are using it, delete if not
class Announcement(models.Model):
    project = models.ForeignKey(ProjectDetails, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recipients = models.ManyToManyField(User, related_name='announcements', blank=True)

    def __str__(self):
        return self.title
    
class ProjectAnnouncement(models.Model):
    project = models.ForeignKey(ProjectDetails, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled Announcement", blank=False)
    message = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recipients = models.ManyToManyField(Membership, through='ProjectAnnouncementRecipient', related_name='project_announcements', blank=False)
    is_urgent = models.BooleanField(default=False,db_index=True)

    class Meta:
        verbose_name = "Project Announcement"
        verbose_name_plural = "Project Announcements"

    def __str__(self):
        title_display = self.title if self.title else "Untitled Announcement"
        return f"{title_display} (Urgent)" if self.is_urgent else title_display
    
    def save(self, *args, **kwargs):
        # Save the announcement first
        super().save(*args, **kwargs)
        # Automatically populate recipients if not already added
        if not self.recipients.exists():
            self.assign_default_recipients()
            
    def assign_default_recipients(self, roles=None):
        """
        Automatically assigns all members of the project as recipients.
        If roles are provided, only members with the specified roles will be assigned.
        """
        try:
            memberships = Membership.objects.filter(project=self.project)

            if roles:
                memberships = memberships.filter(role__name__in=roles)

            for membership in memberships:
                recipient, created = ProjectAnnouncementRecipient.objects.get_or_create(
                    project_announcement=self, membership=membership
                )

        except Exception as e:
            logger.exception(f"Error assigning default recipients for announcement {self.id}")
            raise

    def clean(self):
        if not self.title and not self.message:
            raise ValidationError("Either a title or a message must be provided.")
        
    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
class ProjectAnnouncementRecipient(models.Model):
    project_announcement = models.ForeignKey(ProjectAnnouncement, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.membership} - {self.role}"