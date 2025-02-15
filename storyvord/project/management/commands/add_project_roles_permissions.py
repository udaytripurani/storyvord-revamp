from django.core.management.base import BaseCommand
from django.db import IntegrityError
from ...models import Permission, Role

class Command(BaseCommand):
    help = 'Add project permissions, roles, and assign permissions to roles'

    def handle(self, *args, **kwargs):
        # Define permissions
        permissions = [
            ("generate_project_requirement", "To generate project requirement"),
            ("view", "Can view project"),
            ("edit", "Can edit project"),
            ("add_members", "Can add members to project"),
            ("create_task", "Can create task"),

            # Calendar permissions
            ("create_calander_event", "Can create calendar event"),
            ("view_calander_event", "Can view calendar"),
            ("edit_calander_event", "Can edit calendar"),
            ("delete_calander_event", "Can delete calendar event"),

            # Folder permissions
            ("view_folders", "Can view all folders in a project"),
            ("create_folder", "Can create a folder in a project"),
            ("edit_folder", "Can edit a folder in a project"),
            ("delete_folder", "Can delete a folder in a project"),

            # CallSheet permissions
            ("create_callsheet", "Can create callsheet"),
            ("edit_callsheet", "Can edit callsheet"),
            ("delete_callsheet", "Can delete callsheet"),
        ]

        # Add permissions
        for permission, description in permissions:
            perm, created = Permission.objects.get_or_create(
                name=permission,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Permission added successfully: {permission}'))
            else:
                self.stdout.write(self.style.WARNING(f'Permission already exists: {permission}'))

        # Define roles
        roles = [
            ("admin", "Admin has all the permissions", True),
            ("member", "Can view project", True),
        ]

        # Add roles
        for role, description, is_global in roles:
            try:
                r, created = Role.objects.get_or_create(
                    name=role,
                    defaults={'description': description, 'is_global': is_global}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Role added successfully: {role}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Role already exists: {role}'))
            except IntegrityError:
                # Handle potential race conditions or duplicates
                r = Role.objects.get(name=role)
                self.stdout.write(self.style.WARNING(f'Handled duplicate role: {role}'))

        # Define role-permission relationships
        role_permissions = [
            ("admin", "generate_project_requirement"),
            ("admin", "view"),
            ("admin", "edit"),
            ("admin", "add_members"),
            ("admin", "create_task"),
            ("admin", "create_calander_event"),
            ("admin", "view_calander_event"),
            ("admin", "delete_calander_event"),

            ("admin", "view_folders"),
            ("admin", "create_folder"),
            ("admin", "edit_folder"),
            ("admin", "delete_folder"),

            ("admin", "create_callsheet"),
            ("admin", "edit_callsheet"),
            ("admin", "delete_callsheet"),

            ("admin", "edit_calander_event"),

            ("member", "view_calander_event"),
            ("member", "view"),
        ]

        # Function to add permission to role
        def add_permission_to_role(role_name, permission_name):
            try:
                role = Role.objects.get(name=role_name)
                permission = Permission.objects.get(name=permission_name)
                role.permission.add(permission)  # Ensure Role model has a `permission` ManyToManyField
                self.stdout.write(self.style.SUCCESS(f'Permission {permission_name} added to role {role_name}'))
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Role {role_name} does not exist'))
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Permission {permission_name} does not exist'))

        # Add permissions to roles
        for role, permission in role_permissions:
            add_permission_to_role(role, permission)
