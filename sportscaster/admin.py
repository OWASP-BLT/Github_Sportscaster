from django.contrib import admin
from .models import Channel, MonitoredEntity, GitHubEvent, LeaderboardEntry, Commentary


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'scope', 'is_active', 'created_at']
    list_filter = ['scope', 'is_active']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


@admin.register(MonitoredEntity)
class MonitoredEntityAdmin(admin.ModelAdmin):
    list_display = ['entity_name', 'entity_type', 'channel', 'is_active']
    list_filter = ['entity_type', 'is_active', 'channel']
    search_fields = ['entity_name']


@admin.register(GitHubEvent)
class GitHubEventAdmin(admin.ModelAdmin):
    list_display = ['repository', 'event_type', 'actor', 'timestamp', 'channel', 'processed']
    list_filter = ['event_type', 'processed', 'channel']
    search_fields = ['repository', 'actor']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['repository', 'rank', 'stars', 'forks', 'channel', 'last_updated']
    list_filter = ['channel']
    search_fields = ['repository']
    ordering = ['rank', '-stars']


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ['event', 'text_preview', 'generated_at']
    search_fields = ['text']
    readonly_fields = ['generated_at']
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Commentary'
