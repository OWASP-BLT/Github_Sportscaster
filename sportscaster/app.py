"""Main application for GitHub Sportscaster"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from sportscaster.config import Settings, ChannelConfig
from sportscaster.api import GitHubClient, GitHubEvent
from sportscaster.core import EventMonitor, Leaderboard
from sportscaster.commentary import CommentaryGenerator
from sportscaster.visualization import SportscastRenderer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class Sportscaster:
    """Main GitHub Sportscaster application"""
    
    def __init__(self, settings: Settings):
        """
        Initialize sportscaster
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        
        # Initialize GitHub client
        if not settings.github_token:
            raise ValueError("GitHub token is required")
        
        self.github_client = GitHubClient(settings.github_token)
        
        # Initialize channels
        self.channels: Dict[str, Dict] = {}
        
        for channel_config in settings.channels:
            self._setup_channel(channel_config)
        
        # Shared renderer
        self.renderer = SportscastRenderer()
        
        # Current state
        self.current_commentary = "🎙️ GitHub Sportscaster is starting up! Get ready for live action!"
        self.current_leaderboard = {}
        self.recent_events = []
    
    def _setup_channel(self, channel_config: ChannelConfig):
        """Setup a monitoring channel"""
        logger.info(f"Setting up channel: {channel_config.name}")
        
        # Create monitor
        monitor = EventMonitor(
            self.github_client,
            channel_config,
            self.settings.poll_interval
        )
        
        # Create leaderboard
        leaderboard = Leaderboard(
            self.github_client,
            channel_config.leaderboard_metrics
        )
        
        # Create commentary generator
        use_openai = bool(self.settings.openai_api_key)
        commentary = CommentaryGenerator(
            style=channel_config.commentary_style,
            use_openai=use_openai,
            api_key=self.settings.openai_api_key if use_openai else None
        )
        
        # Register event callback
        def on_event(event: GitHubEvent):
            """Handle new event"""
            # Update leaderboard
            leaderboard.process_event(event)
            
            # Generate commentary
            new_commentary = commentary.generate_commentary(event)
            self.current_commentary = new_commentary
            
            # Update recent events
            self.recent_events.append(event.to_dict())
            if len(self.recent_events) > 50:
                self.recent_events = self.recent_events[-50:]
            
            logger.info(f"Event: {new_commentary}")
        
        monitor.register_callback(on_event)
        
        # Store channel components
        self.channels[channel_config.name] = {
            "config": channel_config,
            "monitor": monitor,
            "leaderboard": leaderboard,
            "commentary": commentary,
        }
    
    async def start(self):
        """Start the sportscaster"""
        logger.info("Starting GitHub Sportscaster...")
        
        if not self.channels:
            logger.warning("No channels configured")
            return
        
        # Start all monitors
        tasks = []
        for channel_name, channel_data in self.channels.items():
            monitor = channel_data["monitor"]
            task = asyncio.create_task(monitor.start())
            tasks.append(task)
        
        # Run leaderboard update loop
        tasks.append(asyncio.create_task(self._leaderboard_update_loop()))
        
        # Wait for all tasks
        await asyncio.gather(*tasks)
    
    async def _leaderboard_update_loop(self):
        """Periodically update leaderboard display"""
        while True:
            try:
                # Update leaderboard data from all channels
                combined_leaderboard = {}
                
                for channel_name, channel_data in self.channels.items():
                    leaderboard = channel_data["leaderboard"]
                    rankings = leaderboard.get_overall_rankings(limit=5)
                    
                    # Merge rankings
                    for key, value in rankings.items():
                        if key not in combined_leaderboard:
                            combined_leaderboard[key] = []
                        combined_leaderboard[key].extend(value)
                
                self.current_leaderboard = combined_leaderboard
                
                # Wait before next update
                await asyncio.sleep(30)
            
            except Exception as e:
                logger.error(f"Error updating leaderboard: {e}", exc_info=True)
                await asyncio.sleep(30)
    
    def get_current_state(self) -> Dict:
        """Get current sportscaster state"""
        return {
            "commentary": self.current_commentary,
            "leaderboard": self.current_leaderboard,
            "recent_events": self.recent_events[-10:],
            "timestamp": datetime.now().isoformat(),
        }
    
    def render_current_frame(self, output_path: Optional[str] = None):
        """
        Render current state as an image
        
        Args:
            output_path: Path to save image (optional)
            
        Returns:
            PIL Image
        """
        img = self.renderer.render_frame(
            commentary=self.current_commentary,
            leaderboard=self.current_leaderboard,
            recent_events=self.recent_events[-10:],
            show_avatars=True
        )
        
        if output_path:
            self.renderer.save_frame(img, output_path)
        
        return img
    
    def stop(self):
        """Stop the sportscaster"""
        logger.info("Stopping GitHub Sportscaster...")
        
        for channel_name, channel_data in self.channels.items():
            monitor = channel_data["monitor"]
            monitor.stop()


async def main():
    """Main entry point"""
    # Load settings
    try:
        settings = Settings.load_from_file("config.yaml")
        logger.info("Loaded configuration from config.yaml")
    except FileNotFoundError:
        logger.info("No config.yaml found, using default settings")
        settings = Settings()
        
        # Add a default channel for demonstration
        if not settings.channels:
            default_channel = ChannelConfig(
                name="default",
                description="Default monitoring channel",
                organizations=[],
                repositories=["octocat/Hello-World"],
                tags=["python"],
            )
            settings.channels.append(default_channel)
    
    # Create and start sportscaster
    sportscaster = Sportscaster(settings)
    
    try:
        await sportscaster.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        sportscaster.stop()


if __name__ == "__main__":
    asyncio.run(main())
