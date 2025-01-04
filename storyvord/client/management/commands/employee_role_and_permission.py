from django.core.management.base import BaseCommand
from ...models import Permission, Role

class Command(BaseCommand):
    help = 'Add client permissions, roles, and assign permissions to roles'

    def handle(self, *args, **kwargs):
        # Define client-specific permissions
        permissions = [
            ("view", "Can view company data"),
            ("edit", "Can edit company data"),
            ("manage_employee", "Can manage employees in a company"),
        
            # folder permissions
            ("view_folder", "Can view company folders"),
            ("create_folder", "Can create folders for company"),
            ("edit_folder", "Can edit company folders"),
            ("delete_folder", "Can delete company folders"),

            # Calendar permissions
            ("view_calendar", "Can view company-specific calendar events"),
            ("create_calendar", "Can create company-specific calendar events"),
            ("edit_calendar", "Can edit company-specific calendar events"),
            ("delete_calendar", "Can delete company-specific calendar events"),
        ]

        # Add permissions
        for permission, description in permissions:
            perm, created = Permission.objects.get_or_create(
                name=permission,
                defaults={"description": description}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Permission added successfully: {permission}'))
            else:
                self.stdout.write(self.style.WARNING(f'Permission already exists: {permission}'))

        # Define client roles
        roles = [
            ("admin", "Admin for the client, has all permissions", False),
            ("employee", "Regular user for the client, limited permissions", False),
        ]

        # Add roles
        for role, description, is_global in roles:
            r, created = Role.objects.get_or_create(
                name=role,
                defaults={"description": description, "is_global": is_global}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Role added successfully: {role}'))
            else:
                self.stdout.write(self.style.WARNING(f'Role already exists: {role}'))

        # Define role-permission relationships for clients
        role_permissions = [
            # Assign permissions to client_admin
            ("admin", "view"),
            ("admin", "edit"),
            ("admin", "manage_employee"),

            # Folder
            ("admin", "view_folder"),
            ("admin", "create_folder"),
            ("admin", "edit_folder"),
            ("admin", "delete_folder"),

            # Calendar
            ("admin", "view_calendar"),
            ("admin", "create_calendar"),
            ("admin", "edit_calendar"),
            ("admin", "delete_calendar"),

            # Employee
            ("employee", "view"),
            ("employee", "view_folder"),
            ("employee", "view_calendar"),
        ]

        # Function to add permission to role
        def add_permission_to_role(role_name, permission_name):
            try:
                role = Role.objects.get(name=role_name)
                permission = Permission.objects.get(name=permission_name)
                role.permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(f'Permission {permission_name} added to role {role_name}'))
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Role {role_name} does not exist'))
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Permission {permission_name} does not exist'))

        # Add permissions to roles
        for role, permission in role_permissions:
            add_permission_to_role(role, permission)

        self.stdout.write(self.style.SUCCESS('Client roles and permissions setup completed successfully.'))