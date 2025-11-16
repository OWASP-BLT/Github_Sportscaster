#!/usr/bin/env python
"""
Quick demo script for GitHub Sportscaster

This script demonstrates the core functionality without requiring
a full setup with GitHub tokens.
"""

from datetime import datetime
from sportscaster.config import ChannelConfig
from sportscaster.commentary import CommentaryGenerator
from sportscaster.api import GitHubEvent
from sportscaster.core import Leaderboard
from sportscaster.visualization import SportscastRenderer
from unittest.mock import Mock


def main():
    """Run a simple demo"""
    print("🎙️ GitHub Sportscaster Demo\n")
    print("=" * 60)
    
    # Create a mock GitHub client
    mock_client = Mock()
    
    # Create sample events
    events = [
        GitHubEvent(
            event_type="star",
            repository="facebook/react",
            actor="johndoe",
            timestamp=datetime.now(),
            data={"action": "starred"},
        ),
        GitHubEvent(
            event_type="fork",
            repository="microsoft/vscode",
            actor="janedoe",
            timestamp=datetime.now(),
            data={"action": "forked"},
        ),
        GitHubEvent(
            event_type="pull_request",
            repository="tensorflow/tensorflow",
            actor="mlexpert",
            timestamp=datetime.now(),
            data={"action": "opened"},
        ),
        GitHubEvent(
            event_type="commit",
            repository="pytorch/pytorch",
            actor="aidev",
            timestamp=datetime.now(),
            data={"action": "pushed"},
        ),
        GitHubEvent(
            event_type="release",
            repository="python/cpython",
            actor="core-dev",
            timestamp=datetime.now(),
            data={"action": "released"},
        ),
    ]
    
    # Test commentary generation
    print("\n1. Testing Commentary Generation")
    print("-" * 60)
    
    styles = ["enthusiastic", "professional", "dramatic"]
    for style in styles:
        print(f"\n   Style: {style.upper()}")
        gen = CommentaryGenerator(style=style)
        
        for event in events[:2]:  # Show first 2 events
            commentary = gen.generate_commentary(event)
            print(f"   {commentary}")
    
    # Test leaderboard
    print("\n\n2. Testing Leaderboard")
    print("-" * 60)
    
    leaderboard = Leaderboard(mock_client, metrics=["star", "fork", "pull_request", "commit"])
    
    # Add more events for leaderboard
    for _ in range(3):
        for event in events:
            leaderboard.process_event(event)
    
    # Show top repositories
    print("\n   Top Repositories by Stars:")
    top_repos = leaderboard.get_top_repositories("star", limit=5)
    for i, entry in enumerate(top_repos, 1):
        print(f"   {i}. {entry['repository']}: {entry['score']}")
    
    # Show top users
    print("\n   Top Users by Activity:")
    top_users = leaderboard.get_top_users("commit", limit=5)
    for i, entry in enumerate(top_users, 1):
        print(f"   {i}. {entry['user']}: {entry['score']}")
    
    # Test visualization
    print("\n\n3. Testing Visualization")
    print("-" * 60)
    
    try:
        renderer = SportscastRenderer(width=1920, height=1080)
        
        # Get leaderboard data
        leaderboard_data = leaderboard.get_overall_rankings(limit=5)
        
        # Generate commentary
        commentary_gen = CommentaryGenerator(style="enthusiastic")
        current_commentary = commentary_gen.generate_commentary(events[0])
        
        # Render a frame
        print("\n   Rendering frame...")
        img = renderer.render_frame(
            commentary=current_commentary,
            leaderboard=leaderboard_data,
            recent_events=[e.to_dict() for e in events],
            show_avatars=True
        )
        
        # Save the frame
        output_path = "/tmp/demo_frame.png"
        renderer.save_frame(img, output_path)
        print(f"   ✓ Frame saved to: {output_path}")
        print(f"   ✓ Image size: {img.size}")
    
    except Exception as e:
        print(f"   ⚠ Visualization demo skipped: {e}")
    
    # Test configuration
    print("\n\n4. Testing Configuration")
    print("-" * 60)
    
    channel = ChannelConfig(
        name="demo-channel",
        description="Demo channel configuration",
        repositories=["owner/repo1", "owner/repo2"],
        event_types=["star", "fork", "pull_request"],
        commentary_style="enthusiastic"
    )
    
    print(f"\n   Channel Name: {channel.name}")
    print(f"   Description: {channel.description}")
    print(f"   Repositories: {', '.join(channel.repositories)}")
    print(f"   Event Types: {', '.join(channel.event_types)}")
    print(f"   Commentary Style: {channel.commentary_style}")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("✓ Demo completed successfully!")
    print("\nNext steps:")
    print("  1. Set up your GitHub token in .env")
    print("  2. Create a config.yaml file (see examples/)")
    print("  3. Run: python -m sportscaster.server")
    print("  4. Open http://localhost:5000 in your browser")
    print("=" * 60)


if __name__ == "__main__":
    main()
