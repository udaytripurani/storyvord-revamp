from django.db import models
from project.models import Project


# Create your models here.

class Folder(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    icon = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', null=True, blank=True) 
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    allowed_users = models.ManyToManyField('accounts.User') 
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='files', null=True, blank=True)

    def __str__(self):
        return self.file.name

    def is_crew_user_allowed(self, user):
        return self.allowed_users.filter(id=user.id, user_type='crew').exists()