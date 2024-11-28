from django.contrib.auth import get_user_model
from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin

@admin.register(AiAgents)
class AiAgentsAdmin(ModelAdmin):
    pass