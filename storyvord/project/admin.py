from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin

# Register your models here.
admin.site.register(OnboardRequest)
admin.site.register(Project)
admin.site.register(LocationDetail)
admin.site.register(SelectCrew)
admin.site.register(SelectEquipment)

@admin.register(Membership)
class MembershipAdmin(ModelAdmin):
    pass

@admin.register(ProjectRequirements)
class ProjectRequirementsAdmin(ModelAdmin):
    pass

@admin.register(ShootingDetails)
class ShootingDetailsAdmin(ModelAdmin):
    pass

@admin.register(ProjectDetails)
class ProjectDetailsAdmin(ModelAdmin):
    list_display = (
        'project_id', 
        'owner', 
        'name', 
        'content_type', 
        'brief', 
        'additional_details', 
        'created_at', 
        'updated_at'
    )
    filter_horizontal = ('members',)
    
