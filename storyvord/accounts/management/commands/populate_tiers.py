from django.core.management.base import BaseCommand
from accounts.models import Tier, UserType

class Command(BaseCommand):
    help = 'Populate the default tier lists'

    def handle(self, *args, **kwargs):
        tiers = [
            {'name': 'Free', 'description': 'Free tier with limited features', 'is_default': True, 'user_type': UserType.objects.get(name='client')},
            {'name': 'Basic', 'description': 'Basic tier with standard features', 'user_type': UserType.objects.get(name='client')},
            {'name': 'Premium', 'description': 'Premium tier with all features', 'user_type': UserType.objects.get(name='client')},
            {'name': 'Free', 'description': 'Free tier with limited features', 'is_default': True, 'user_type': UserType.objects.get(name='crew')},
            {'name': 'Basic', 'description': 'Basic tier with standard features', 'user_type': UserType.objects.get(name='crew')},
            {'name': 'Premium', 'description': 'Premium tier with all features', 'user_type': UserType.objects.get(name='crew')},
        ]

        for tier_data in tiers:
            try:
                tier, created = Tier.objects.get_or_create(name=tier_data['name'], user_type=tier_data['user_type'], defaults=tier_data)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created tier: {tier.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Tier already exists: {tier.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating tier: {e}'))
