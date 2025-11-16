from django.db import models
from django.utils import timezone


class Channel(models.Model):
    """Represents a curated channel for monitoring specific GitHub entities"""
    SCOPE_CHOICES = [
        ('all', 'All GitHub'),
        ('org', 'Organization'),
        ('repo', 'Repository'),
        ('tag', 'Tag'),
        ('custom', 'Custom List'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class MonitoredEntity(models.Model):
    """Represents a GitHub entity being monitored (org, repo, etc.)"""
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='entities')
    entity_type = models.CharField(max_length=20)  # 'org', 'repo', 'tag'
    entity_name = models.CharField(max_length=500)  # e.g., 'facebook/react'
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['channel', 'entity_name']
    
    def __str__(self):
        return f"{self.entity_type}: {self.entity_name}"


class GitHubEvent(models.Model):
    """Stores GitHub events captured by the sportscaster"""
    EVENT_TYPES = [
        ('star', 'Star'),
        ('fork', 'Fork'),
        ('pull_request', 'Pull Request'),
        ('commit', 'Commit'),
        ('release', 'Release'),
        ('issue', 'Issue'),
        ('watch', 'Watch'),
    ]
    
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    repository = models.CharField(max_length=500)
    actor = models.CharField(max_length=200, blank=True)
    actor_avatar = models.URLField(blank=True)
    event_data = models.JSONField()
    timestamp = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'channel']),
            models.Index(fields=['processed']),
        ]
    
    def __str__(self):
        return f"{self.event_type} on {self.repository} at {self.timestamp}"


class LeaderboardEntry(models.Model):
    """Tracks leaderboard metrics for repositories"""
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='leaderboard')
    repository = models.CharField(max_length=500)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    pull_requests = models.IntegerField(default=0)
    commits = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['channel', 'repository']
        ordering = ['-stars', '-forks']
    
    def __str__(self):
        return f"{self.repository} (Rank: {self.rank})"


class Commentary(models.Model):
    """Stores AI-generated commentary for events"""
    event = models.OneToOneField(GitHubEvent, on_delete=models.CASCADE, related_name='commentary')
    text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Commentary for {self.event}"
