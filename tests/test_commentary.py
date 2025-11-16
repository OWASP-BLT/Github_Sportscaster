"""Tests for commentary generation"""

import pytest
from datetime import datetime
from sportscaster.commentary import CommentaryGenerator
from sportscaster.api import GitHubEvent


def test_commentary_generator_creation():
    """Test creating a commentary generator"""
    gen = CommentaryGenerator(style="enthusiastic")
    assert gen.style == "enthusiastic"


def test_generate_commentary_star():
    """Test generating commentary for star event"""
    gen = CommentaryGenerator(style="enthusiastic")
    
    event = GitHubEvent(
        event_type="star",
        repository="owner/repo",
        actor="testuser",
        timestamp=datetime.now()
    )
    
    commentary = gen.generate_commentary(event)
    
    assert "testuser" in commentary
    assert "owner/repo" in commentary
    assert len(commentary) > 0


def test_generate_commentary_fork():
    """Test generating commentary for fork event"""
    gen = CommentaryGenerator(style="professional")
    
    event = GitHubEvent(
        event_type="fork",
        repository="owner/repo",
        actor="testuser",
        timestamp=datetime.now()
    )
    
    commentary = gen.generate_commentary(event)
    
    assert "testuser" in commentary
    assert "owner/repo" in commentary


def test_commentary_styles():
    """Test different commentary styles"""
    event = GitHubEvent(
        event_type="star",
        repository="owner/repo",
        actor="testuser",
        timestamp=datetime.now()
    )
    
    styles = ["enthusiastic", "professional", "dramatic"]
    
    for style in styles:
        gen = CommentaryGenerator(style=style)
        commentary = gen.generate_commentary(event)
        assert len(commentary) > 0


def test_set_style():
    """Test changing commentary style"""
    gen = CommentaryGenerator(style="enthusiastic")
    assert gen.style == "enthusiastic"
    
    gen.set_style("professional")
    assert gen.style == "professional"


def test_leaderboard_commentary():
    """Test leaderboard commentary generation"""
    gen = CommentaryGenerator()
    
    leaderboard = {
        "top_repos_stars": [
            {"repository": "owner/repo", "score": 100}
        ]
    }
    
    commentary = gen.generate_leaderboard_commentary(leaderboard)
    assert len(commentary) > 0
