from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Channel, GitHubEvent, LeaderboardEntry, MonitoredEntity
from .services import GitHubService, EventProcessor
from .ai_commentary import AICommentator
import json


def index(request):
    """Main sportscaster view"""
    channels = Channel.objects.filter(is_active=True)
    return render(request, 'sportscaster/index.html', {'channels': channels})


def channel_view(request, channel_id):
    """View for a specific channel"""
    channel = get_object_or_404(Channel, id=channel_id, is_active=True)
    return render(request, 'sportscaster/channel.html', {'channel': channel})


@api_view(['GET'])
def api_channels(request):
    """API endpoint to list all channels"""
    channels = Channel.objects.filter(is_active=True)
    data = [{
        'id': ch.id,
        'name': ch.name,
        'description': ch.description,
        'scope': ch.scope,
    } for ch in channels]
    return Response(data)


@api_view(['GET'])
def api_channel_events(request, channel_id):
    """API endpoint to get events for a channel"""
    channel = get_object_or_404(Channel, id=channel_id)
    limit = int(request.GET.get('limit', 50))
    
    events = GitHubEvent.objects.filter(channel=channel)[:limit]
    data = [{
        'id': event.id,
        'event_type': event.event_type,
        'repository': event.repository,
        'actor': event.actor,
        'actor_avatar': event.actor_avatar,
        'timestamp': event.timestamp.isoformat(),
        'commentary': getattr(event.commentary, 'text', '') if hasattr(event, 'commentary') else '',
    } for event in events]
    
    return Response(data)


@api_view(['GET'])
def api_leaderboard(request, channel_id):
    """API endpoint to get leaderboard for a channel"""
    channel = get_object_or_404(Channel, id=channel_id)
    limit = int(request.GET.get('limit', 10))
    
    entries = LeaderboardEntry.objects.filter(channel=channel).order_by('-stars', '-forks')[:limit]
    data = [{
        'repository': entry.repository,
        'stars': entry.stars,
        'forks': entry.forks,
        'pull_requests': entry.pull_requests,
        'commits': entry.commits,
        'rank': idx + 1,
    } for idx, entry in enumerate(entries)]
    
    return Response(data)


@api_view(['POST'])
def api_test_commentary(request):
    """Test endpoint for AI commentary generation"""
    event_data = request.data
    
    commentator = AICommentator()
    commentary = commentator.generate_commentary(event_data)
    
    return Response({
        'commentary': commentary,
        'event': event_data,
    })
