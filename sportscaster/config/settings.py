"""Settings and configuration management"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import yaml

load_dotenv()


class ChannelConfig(BaseModel):
    """Configuration for a sportscaster channel"""
    
    name: str = Field(..., description="Channel name")
    description: str = Field(default="", description="Channel description")
    
    # Source configurations
    organizations: List[str] = Field(default_factory=list, description="GitHub organizations to monitor")
    repositories: List[str] = Field(default_factory=list, description="Repositories in format 'owner/repo'")
    tags: List[str] = Field(default_factory=list, description="Tags/topics to monitor")
    curated_lists: List[str] = Field(default_factory=list, description="Curated repository lists")
    
    # Event filters
    event_types: List[str] = Field(
        default_factory=lambda: ["star", "fork", "pull_request", "commit", "issue", "release"],
        description="Types of events to monitor"
    )
    
    # Leaderboard settings
    leaderboard_metrics: List[str] = Field(
        default_factory=lambda: ["stars", "forks", "pull_requests", "commits"],
        description="Metrics to track in leaderboard"
    )
    
    # Commentary settings
    commentary_style: str = Field(default="enthusiastic", description="Style of AI commentary")
    
    # Display settings
    show_avatars: bool = Field(default=True, description="Show user avatars")
    show_logos: bool = Field(default=True, description="Show project logos")


class Settings(BaseModel):
    """Global application settings"""
    
    # API credentials
    github_token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    
    # Polling configuration
    poll_interval: int = Field(default_factory=lambda: int(os.getenv("POLL_INTERVAL", "60")))
    max_events_per_cycle: int = Field(default_factory=lambda: int(os.getenv("MAX_EVENTS_PER_CYCLE", "50")))
    
    # Server configuration
    flask_host: str = Field(default_factory=lambda: os.getenv("FLASK_HOST", "0.0.0.0"))
    flask_port: int = Field(default_factory=lambda: int(os.getenv("FLASK_PORT", "5000")))
    
    # Channels
    channels: List[ChannelConfig] = Field(default_factory=list)
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "Settings":
        """Load settings from a YAML configuration file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str) -> None:
        """Save settings to a YAML configuration file"""
        with open(config_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
