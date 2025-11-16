"""
Django management command to monitor GitHub events and broadcast them via WebSocket
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import logging
from sportscaster.models import Channel, MonitoredEntity, GitHubEvent, LeaderboardEntry, Commentary
from sportscaster.services import GitHubService, EventProcessor
from sportscaster.ai_commentary import AICommentator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor GitHub events and broadcast them to WebSocket clients'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=settings.POLL_INTERVAL,
            help='Polling interval in seconds'
        )
        parser.add_argument(
            '--channel-id',
            type=int,
            help='Monitor specific channel ID only'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        channel_id = options.get('channel_id')
        
        self.stdout.write(self.style.SUCCESS('Starting GitHub Sportscaster monitoring...'))
        
        github_service = GitHubService()
        event_processor = EventProcessor()
        commentator = AICommentator()
        channel_layer = get_channel_layer()
        
        while True:
            try:
                # Get active channels to monitor
                channels_query = Channel.objects.filter(is_active=True)
                if channel_id:
                    channels_query = channels_query.filter(id=channel_id)
                
                channels = channels_query.all()
                
                for channel in channels:
                    self.stdout.write(f'Processing channel: {channel.name}')
                    
                    # Get monitored entities for this channel
                    entities = MonitoredEntity.objects.filter(
                        channel=channel,
                        is_active=True
                    )
                    
                    for entity in entities:
                        self.process_entity(
                            entity,
                            github_service,
                            event_processor,
                            commentator,
                            channel_layer
                        )
                    
                    # Update leaderboard
                    self.update_leaderboard(channel, github_service, channel_layer)
                
                self.stdout.write(self.style.SUCCESS(f'Completed monitoring cycle. Sleeping for {interval} seconds...'))
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Monitoring stopped by user'))
                break
            except Exception as e:
                logger.error(f'Error in monitoring loop: {e}', exc_info=True)
                time.sleep(interval)
    
    def process_entity(self, entity, github_service, event_processor, commentator, channel_layer):
        """Process events for a monitored entity"""
        try:
            # Parse entity name (e.g., "owner/repo")
            if entity.entity_type == 'repo':
                parts = entity.entity_name.split('/')
                if len(parts) != 2:
                    logger.warning(f'Invalid repo format: {entity.entity_name}')
                    return
                
                owner, repo = parts
                events = github_service.get_repository_events(owner, repo, per_page=10)
                
                for raw_event in events:
                    processed_event = event_processor.process_event(raw_event)
                    if not processed_event:
                        continue
                    
                    # Check if event already exists (basic deduplication)
                    event_id = raw_event.get('id')
                    if GitHubEvent.objects.filter(
                        channel=entity.channel,
                        event_data__id=event_id
                    ).exists():
                        continue
                    
                    # Create event in database
                    github_event = GitHubEvent.objects.create(
                        channel=entity.channel,
                        event_type=processed_event['event_type'],
                        repository=processed_event['repository'],
                        actor=processed_event['actor'],
                        actor_avatar=processed_event['actor_avatar'],
                        event_data=raw_event,
                    )
                    
                    # Generate AI commentary
                    commentary_text = commentator.generate_commentary(processed_event)
                    Commentary.objects.create(
                        event=github_event,
                        text=commentary_text
                    )
                    
                    # Broadcast event via WebSocket
                    room_group_name = f'sportscaster_{entity.channel.id}'
                    async_to_sync(channel_layer.group_send)(
                        room_group_name,
                        {
                            'type': 'event_message',
                            'data': {
                                'type': 'event',
                                'event_type': github_event.event_type,
                                'repository': github_event.repository,
                                'actor': github_event.actor,
                                'actor_avatar': github_event.actor_avatar,
                                'timestamp': github_event.timestamp.isoformat(),
                                'commentary': commentary_text,
                            }
                        }
                    )
                    
                    github_event.processed = True
                    github_event.save()
                    
                    self.stdout.write(f'  ✓ Processed: {github_event.event_type} on {github_event.repository}')
        
        except Exception as e:
            logger.error(f'Error processing entity {entity.entity_name}: {e}', exc_info=True)
    
    def update_leaderboard(self, channel, github_service, channel_layer):
        """Update leaderboard for a channel"""
        try:
            entities = MonitoredEntity.objects.filter(
                channel=channel,
                is_active=True,
                entity_type='repo'
            )
            
            leaderboard_data = []
            
            for entity in entities:
                parts = entity.entity_name.split('/')
                if len(parts) != 2:
                    continue
                
                owner, repo = parts
                stats = github_service.get_repository_stats(owner, repo)
                
                if stats:
                    entry, created = LeaderboardEntry.objects.update_or_create(
                        channel=channel,
                        repository=entity.entity_name,
                        defaults={
                            'stars': stats.get('stars', 0),
                            'forks': stats.get('forks', 0),
                        }
                    )
                    
                    leaderboard_data.append({
                        'repository': entry.repository,
                        'stars': entry.stars,
                        'forks': entry.forks,
                        'pull_requests': entry.pull_requests,
                        'commits': entry.commits,
                    })
            
            # Sort and assign ranks
            leaderboard_data.sort(key=lambda x: (x['stars'], x['forks']), reverse=True)
            
            for idx, entry_data in enumerate(leaderboard_data):
                LeaderboardEntry.objects.filter(
                    channel=channel,
                    repository=entry_data['repository']
                ).update(rank=idx + 1)
                entry_data['rank'] = idx + 1
            
            # Broadcast leaderboard update
            room_group_name = f'sportscaster_{channel.id}'
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'leaderboard_update',
                    'data': {
                        'type': 'leaderboard',
                        'leaderboard': leaderboard_data[:10]  # Top 10
                    }
                }
            )
            
            self.stdout.write(f'  ✓ Updated leaderboard for {channel.name}')
        
        except Exception as e:
            logger.error(f'Error updating leaderboard: {e}', exc_info=True)
