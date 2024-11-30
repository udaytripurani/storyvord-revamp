from django.db import models
from project.models import ProjectDetails, Membership


# Create your models here.

class Folder(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    icon = models.TextField()
    project = models.ForeignKey(ProjectDetails, on_delete=models.CASCADE, related_name='files') 
    allowed_users = models.ManyToManyField(Membership, related_name='allowed_folders', blank=True) 
    default = models.BooleanField(default=False)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_folders')

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='files', null=True, blank=True)

    def __str__(self):
        return self.file.name