"""Tests for leaderboard tracking"""

import pytest
from datetime import datetime
from unittest.mock import Mock
from sportscaster.core import Leaderboard
from sportscaster.api import GitHubEvent


def test_leaderboard_creation():
    """Test creating a leaderboard"""
    client = Mock()
    leaderboard = Leaderboard(client, metrics=["stars", "forks"])
    
    assert "stars" in leaderboard.metrics
    assert "forks" in leaderboard.metrics


def test_process_event():
    """Test processing an event"""
    client = Mock()
    leaderboard = Leaderboard(client)
    
    event = GitHubEvent(
        event_type="star",
        repository="owner/repo",
        actor="testuser",
        timestamp=datetime.now()
    )
    
    leaderboard.process_event(event)
    
    # Check that scores were updated
    assert leaderboard.user_scores["testuser"]["star"] == 1
    assert leaderboard.repository_scores["owner/repo"]["star"] == 1


def test_process_multiple_events():
    """Test processing multiple events"""
    client = Mock()
    leaderboard = Leaderboard(client)
    
    # Process multiple events
    for i in range(5):
        event = GitHubEvent(
            event_type="star",
            repository="owner/repo",
            actor="testuser",
            timestamp=datetime.now()
        )
        leaderboard.process_event(event)
    
    assert leaderboard.user_scores["testuser"]["star"] == 5
    assert leaderboard.repository_scores["owner/repo"]["star"] == 5


def test_get_top_repositories():
    """Test getting top repositories"""
    client = Mock()
    leaderboard = Leaderboard(client, metrics=["star"])
    
    # Add some events
    for i in range(3):
        event = GitHubEvent(
            event_type="star",
            repository=f"owner/repo{i}",
            actor="testuser",
            timestamp=datetime.now()
        )
        leaderboard.process_event(event)
    
    top = leaderboard.get_top_repositories("star", limit=2)
    assert len(top) <= 2


def test_get_top_users():
    """Test getting top users"""
    client = Mock()
    leaderboard = Leaderboard(client, metrics=["commit"])
    
    # Add events from different users
    for i in range(3):
        event = GitHubEvent(
            event_type="commit",
            repository="owner/repo",
            actor=f"user{i}",
            timestamp=datetime.now()
        )
        leaderboard.process_event(event)
    
    top = leaderboard.get_top_users("commit", limit=2)
    assert len(top) <= 2


def test_reset():
    """Test resetting leaderboard"""
    client = Mock()
    leaderboard = Leaderboard(client)
    
    # Add an event
    event = GitHubEvent(
        event_type="star",
        repository="owner/repo",
        actor="testuser",
        timestamp=datetime.now()
    )
    leaderboard.process_event(event)
    
    # Reset
    leaderboard.reset()
    
    # Check that scores are cleared
    assert len(leaderboard.user_scores.get("star", {})) == 0
    assert len(leaderboard.repository_scores.get("star", {})) == 0


def test_get_stats():
    """Test getting leaderboard statistics"""
    client = Mock()
    leaderboard = Leaderboard(client, metrics=["stars", "forks"])
    
    stats = leaderboard.get_stats()
    
    assert "tracked_metrics" in stats
    assert "last_update" in stats
    assert stats["tracked_metrics"] == ["stars", "forks"]
