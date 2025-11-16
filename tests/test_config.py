"""Tests for configuration module"""

import pytest
from sportscaster.config import Settings, ChannelConfig


def test_channel_config_creation():
    """Test creating a channel configuration"""
    channel = ChannelConfig(
        name="test",
        description="Test channel",
        repositories=["owner/repo"],
        event_types=["star", "fork"]
    )
    
    assert channel.name == "test"
    assert channel.description == "Test channel"
    assert "owner/repo" in channel.repositories
    assert "star" in channel.event_types


def test_channel_config_defaults():
    """Test channel configuration defaults"""
    channel = ChannelConfig(name="test")
    
    assert channel.name == "test"
    assert channel.description == ""
    assert len(channel.organizations) == 0
    assert len(channel.repositories) == 0
    assert "star" in channel.event_types
    assert channel.show_avatars is True


def test_settings_creation():
    """Test creating settings"""
    settings = Settings()
    
    assert settings.poll_interval == 60
    assert settings.flask_port == 5000
    assert len(settings.channels) == 0


def test_settings_with_channels():
    """Test settings with channels"""
    channel = ChannelConfig(name="test", repositories=["owner/repo"])
    settings = Settings(channels=[channel])
    
    assert len(settings.channels) == 1
    assert settings.channels[0].name == "test"
