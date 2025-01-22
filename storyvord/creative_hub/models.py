import os
from django.db import models
from accounts.models import User
from project.models import ProjectDetails
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

class Script(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectDetails, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)  # Script content (if created in frontend)
    file = models.FileField(upload_to='scripts/', blank=True, null=True)  # File upload (if uploaded)
    suggestions = models.JSONField(default=list)  # Stores AI suggestions
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.project.name}"

class Scene(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="scenes", null=True, blank=True)
    scene_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()  # Scene summary
    location = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField()  # Order of the scene in the script
    timeline = models.JSONField(default=dict)  # Start and end timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Scene {self.order} - {self.script.title}"


class Shot(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name="shots")
    description = models.TextField()  # Shot details
    type = models.CharField(max_length=50, choices=[
        ("Close-Up", "Close-Up"),
        ("Wide Shot", "Wide Shot"),
        ("Tracking Shot", "Tracking Shot"),
        ("Over-The-Shoulder", "Over-The-Shoulder"),
        ("Other", "Other"),
    ])
    order = models.PositiveIntegerField()  # Order within the scene
    done = models.BooleanField(default=False)
    timeline = models.JSONField(default=dict)  # Start and end timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Shot {self.order} - {self.scene}"
    
class Sequence(models.Model):
    project = models.ForeignKey(ProjectDetails, on_delete=models.CASCADE, related_name="sequences")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    scenes = models.ManyToManyField(Scene, related_name="sequences")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sequence: {self.name} - {self.project.name}"


class Storyboard(models.Model):
    scene = models.OneToOneField(Scene, on_delete=models.CASCADE, related_name="storyboard", null=True, blank=True)
    shot = models.OneToOneField(Shot, on_delete=models.CASCADE, related_name="storyboard", null=True, blank=True)
    image_url = models.URLField()  # URL of the storyboard image
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.scene:
            return f"Storyboard for Scene {self.scene.order}"
        if self.shot:
            return f"Storyboard for Shot {self.shot.order}"
        return "Storyboard"