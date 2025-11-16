"""Event monitoring and collection"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
from collections import deque

from sportscaster.api import GitHubClient, GitHubEvent
from sportscaster.config import ChannelConfig

logger = logging.getLogger(__name__)


class EventMonitor:
    """Monitors GitHub activity and collects events"""
    
    def __init__(self, client: GitHubClient, channel_config: ChannelConfig, poll_interval: int = 60):
        """
        Initialize event monitor
        
        Args:
            client: GitHub API client
            channel_config: Channel configuration
            poll_interval: Seconds between polling cycles
        """
        self.client = client
        self.config = channel_config
        self.poll_interval = poll_interval
        
        self.event_queue: deque = deque(maxlen=1000)
        self.last_poll_time: Optional[datetime] = None
        self.is_running = False
        
        self.repositories: List[str] = []
        self._initialize_repositories()
        
        # Event callbacks
        self.event_callbacks: List[Callable[[GitHubEvent], None]] = []
    
    def _initialize_repositories(self):
        """Initialize list of repositories to monitor"""
        # Add explicitly configured repositories
        self.repositories.extend(self.config.repositories)
        
        # Add repositories from organizations
        for org in self.config.organizations:
            logger.info(f"Fetching repositories for organization: {org}")
            org_repos = self.client.get_org_repositories(org)
            self.repositories.extend([repo.full_name for repo in org_repos])
        
        # Add repositories by tags/topics
        for tag in self.config.tags:
            logger.info(f"Searching repositories by topic: {tag}")
            tag_repos = self.client.search_repositories_by_topic(tag, max_results=10)
            self.repositories.extend(tag_repos)
        
        # Remove duplicates
        self.repositories = list(set(self.repositories))
        logger.info(f"Monitoring {len(self.repositories)} repositories")
    
    def register_callback(self, callback: Callable[[GitHubEvent], None]):
        """Register a callback to be called when new events are detected"""
        self.event_callbacks.append(callback)
    
    async def start(self):
        """Start monitoring for events"""
        self.is_running = True
        logger.info(f"Starting event monitor for channel: {self.config.name}")
        
        while self.is_running:
            try:
                await self._poll_events()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info(f"Stopping event monitor for channel: {self.config.name}")
    
    async def _poll_events(self):
        """Poll for new events from monitored repositories"""
        since = self.last_poll_time or datetime.now() - timedelta(hours=1)
        new_events: List[GitHubEvent] = []
        
        logger.info(f"Polling events since {since}")
        
        # Collect events from all monitored repositories
        for repo_name in self.repositories:
            try:
                events = self.client.get_repository_events(
                    repo_name,
                    since=since,
                    event_types=self.config.event_types
                )
                
                # Also get stargazer activity if monitoring stars
                if "star" in self.config.event_types:
                    star_events = self.client.get_stargazers_activity(repo_name, since=since)
                    events.extend(star_events)
                
                new_events.extend(events)
            
            except Exception as e:
                logger.error(f"Error polling repository {repo_name}: {e}")
        
        # Sort events by timestamp
        new_events.sort(key=lambda e: e.timestamp)
        
        # Add to queue and trigger callbacks
        for event in new_events:
            self.event_queue.append(event)
            
            # Trigger all registered callbacks
            for callback in self.event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}", exc_info=True)
        
        self.last_poll_time = datetime.now()
        logger.info(f"Collected {len(new_events)} new events")
    
    def get_recent_events(self, limit: int = 50) -> List[GitHubEvent]:
        """
        Get most recent events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return list(self.event_queue)[-limit:]
    
    def get_event_counts(self) -> Dict[str, int]:
        """
        Get counts of events by type
        
        Returns:
            Dictionary mapping event type to count
        """
        counts = {}
        for event in self.event_queue:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts
