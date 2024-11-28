from django.contrib.auth import get_user_model
from .models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    ordering = ["created_at"]
    list_display = [
        "display_header",
        "is_active",
        "display_staff",
        "display_superuser",
        "display_created",
    ]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": ("steps",),
                "classes": ["tab"],
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["tab"],
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (),
                "classes": ["tab"],
            },
        ),
    )
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    readonly_fields = ["created_at", "updated_at"]

    @display(description=_("User"))
    def display_header(self, instance: User):
        return instance.email

    @display(description=_("Staff"), boolean=True)
    def display_staff(self, instance: User):
        return instance.is_staff

    @display(description=_("Superuser"), boolean=True)
    def display_superuser(self, instance: User):
        return instance.is_superuser

    @display(description=_("Created"))
    def display_created(self, instance: User):
        return instance.created_at

@admin.register(PersonalInfo)
class UserProfileAdmin(ModelAdmin):
    search_fields = ["full_name", "email", "bio"]
    list_display = ["full_name","contact_number","location","job_title","bio"]
    fieldsets = (
        (None, {"fields": ("full_name", "bio")}),
        (
            _("Important dates"),
            {
                "fields": (),
                "classes": ["tab"],
            },
        ),
    )
    # readonly_fields = ["created_at", "updated_at"]
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    @display(description=_("Created"))
    def display_created(self, instance: PersonalInfo):
        return instance.created_at

@admin.register(UserType)
class UserTypeAdmin(ModelAdmin):
    pass