"""
Django management command to set up demo data for testing
"""
from django.core.management.base import BaseCommand
from sportscaster.models import Channel, MonitoredEntity
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up demo data for the sportscaster'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up demo data...'))
        
        # Create demo channels
        channel1, created = Channel.objects.get_or_create(
            name="Hot Python Projects",
            defaults={
                'description': "Monitoring trending Python repositories",
                'scope': 'custom',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Created channel: {channel1.name}')
            
            # Add repositories to monitor
            repos = [
                'psf/requests',
                'django/django',
                'pallets/flask',
                'python/cpython',
                'pandas-dev/pandas'
            ]
            
            for repo_name in repos:
                entity, entity_created = MonitoredEntity.objects.get_or_create(
                    channel=channel1,
                    entity_name=repo_name,
                    defaults={
                        'entity_type': 'repo',
                        'is_active': True
                    }
                )
                if entity_created:
                    self.stdout.write(f'    - Added repository: {repo_name}')
        else:
            self.stdout.write(f'  ℹ Channel already exists: {channel1.name}')
        
        # Create second demo channel
        channel2, created = Channel.objects.get_or_create(
            name="JavaScript Frameworks",
            defaults={
                'description': "Monitoring popular JavaScript frameworks",
                'scope': 'custom',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Created channel: {channel2.name}')
            
            repos = [
                'facebook/react',
                'vuejs/vue',
                'angular/angular',
                'sveltejs/svelte',
                'vercel/next.js'
            ]
            
            for repo_name in repos:
                entity, entity_created = MonitoredEntity.objects.get_or_create(
                    channel=channel2,
                    entity_name=repo_name,
                    defaults={
                        'entity_type': 'repo',
                        'is_active': True
                    }
                )
                if entity_created:
                    self.stdout.write(f'    - Added repository: {repo_name}')
        else:
            self.stdout.write(f'  ℹ Channel already exists: {channel2.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Demo data setup complete!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('  1. Start the server: python manage.py runserver')
        self.stdout.write('  2. Start monitoring: python manage.py monitor_github')
        self.stdout.write('  3. Visit http://localhost:8000 to see the sportscaster in action')
