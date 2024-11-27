from django.db import models

from accounts.models import User
from project.models import ProjectDetails, Membership
from django.core.exceptions import ValidationError

# Create your models here.
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