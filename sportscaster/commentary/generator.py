"""AI-powered commentary generation"""

import logging
from typing import List, Dict, Any, Optional
import random

from sportscaster.api import GitHubEvent

logger = logging.getLogger(__name__)


class CommentaryGenerator:
    """Generates AI-powered sportscaster commentary for GitHub events"""
    
    def __init__(self, style: str = "enthusiastic", use_openai: bool = False, api_key: Optional[str] = None):
        """
        Initialize commentary generator
        
        Args:
            style: Commentary style (enthusiastic, professional, casual, dramatic)
            use_openai: Whether to use OpenAI API for enhanced commentary
            api_key: OpenAI API key (required if use_openai is True)
        """
        self.style = style
        self.use_openai = use_openai
        
        # Initialize OpenAI if requested
        self.openai_client = None
        if use_openai and api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI commentary enabled")
            except ImportError:
                logger.warning("OpenAI package not installed, falling back to template-based commentary")
                self.use_openai = False
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.use_openai = False
        
        # Template-based commentary patterns
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load commentary templates by event type and style"""
        
        enthusiastic = {
            "star": [
                "🌟 INCREDIBLE! {actor} just starred {repository}! The crowd goes wild!",
                "🎯 YES! Another star for {repository} from {actor}! What a moment!",
                "⭐ AMAZING! {actor} has given {repository} a star! The energy is electric!",
                "🔥 OH MY! {repository} gets another star from {actor}! Unstoppable!",
            ],
            "fork": [
                "🍴 UNBELIEVABLE! {actor} just forked {repository}! This project is on fire!",
                "💥 WOW! {repository} has been forked by {actor}! The community loves it!",
                "🚀 FANTASTIC! {actor} forked {repository}! The innovation continues!",
            ],
            "pull_request": [
                "📝 BREAKING! {actor} opened a pull request in {repository}! Contributions are flowing!",
                "💪 OUTSTANDING! {actor} submits a PR to {repository}! Teamwork in action!",
                "🎉 EXCITING! A new pull request from {actor} in {repository}!",
            ],
            "commit": [
                "💻 PHENOMENAL! {actor} just pushed commits to {repository}! The code is evolving!",
                "⚡ LIGHTNING FAST! {actor} commits to {repository}! Development never stops!",
                "🔨 BRILLIANT! New commits from {actor} in {repository}!",
            ],
            "issue": [
                "🐛 ATTENTION! {actor} opened an issue in {repository}! Community engagement!",
                "📋 NOTABLE! {actor} reports an issue in {repository}! Quality matters!",
            ],
            "release": [
                "🎊 HISTORIC! {repository} just released a new version! {actor} leads the charge!",
                "🚀 MAJOR MILESTONE! {repository} drops a new release! The crowd erupts!",
            ],
        }
        
        professional = {
            "star": [
                "⭐ {repository} receives a star from {actor}.",
                "🌟 {actor} has starred {repository}.",
            ],
            "fork": [
                "🍴 {actor} has forked {repository}.",
                "📂 {repository} forked by {actor}.",
            ],
            "pull_request": [
                "📝 {actor} opened a pull request in {repository}.",
                "🔄 New pull request from {actor} in {repository}.",
            ],
            "commit": [
                "💻 {actor} pushed commits to {repository}.",
                "📊 New commits in {repository} by {actor}.",
            ],
            "issue": [
                "🐛 {actor} opened an issue in {repository}.",
                "📋 Issue reported by {actor} in {repository}.",
            ],
            "release": [
                "🚀 {repository} published a new release.",
                "📦 New release available for {repository}.",
            ],
        }
        
        dramatic = {
            "star": [
                "✨ In a stunning turn of events, {actor} bestows a star upon {repository}!",
                "🌟 The tale unfolds as {actor} illuminates {repository} with a star!",
            ],
            "fork": [
                "🍴 The saga continues! {actor} has forked the legendary {repository}!",
                "⚡ A new chapter begins as {actor} forks {repository}!",
            ],
            "pull_request": [
                "📜 A bold move! {actor} submits their contribution to {repository}!",
                "🎭 The plot thickens as {actor} opens a pull request in {repository}!",
            ],
            "commit": [
                "💫 The journey evolves! {actor} commits to {repository}!",
                "🌊 Waves of change as {actor} pushes to {repository}!",
            ],
            "issue": [
                "⚠️ A challenge emerges! {actor} raises an issue in {repository}!",
                "🔍 Discovery! {actor} identifies an issue in {repository}!",
            ],
            "release": [
                "🎆 A momentous occasion! {repository} unveils a new release!",
                "👑 Triumph! {repository} achieves a new milestone with this release!",
            ],
        }
        
        return {
            "enthusiastic": enthusiastic,
            "professional": professional,
            "dramatic": dramatic,
            "casual": professional,  # Fallback to professional
        }
    
    def generate_commentary(self, event: GitHubEvent) -> str:
        """
        Generate commentary for an event
        
        Args:
            event: GitHub event
            
        Returns:
            Commentary string
        """
        if self.use_openai and self.openai_client:
            return self._generate_ai_commentary(event)
        else:
            return self._generate_template_commentary(event)
    
    def _generate_template_commentary(self, event: GitHubEvent) -> str:
        """Generate commentary using templates"""
        style_templates = self.templates.get(self.style, self.templates["enthusiastic"])
        event_templates = style_templates.get(event.event_type, [
            f"📢 {event.actor} performed {event.event_type} in {event.repository}!"
        ])
        
        template = random.choice(event_templates)
        return template.format(
            actor=event.actor,
            repository=event.repository,
            event_type=event.event_type,
        )
    
    def _generate_ai_commentary(self, event: GitHubEvent) -> str:
        """Generate commentary using OpenAI API"""
        try:
            prompt = f"""You are an enthusiastic sports commentator for GitHub activity.
Generate a short, {self.style} commentary (1-2 sentences) for this GitHub event:

Event Type: {event.event_type}
Repository: {event.repository}
Actor: {event.actor}

Make it exciting and engaging, as if you're announcing it to a live audience!"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an enthusiastic GitHub sports commentator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating AI commentary: {e}")
            return self._generate_template_commentary(event)
    
    def generate_leaderboard_commentary(self, leaderboard_data: Dict[str, Any]) -> str:
        """
        Generate commentary for leaderboard updates
        
        Args:
            leaderboard_data: Leaderboard data
            
        Returns:
            Commentary string
        """
        if not leaderboard_data:
            return "📊 The competition is heating up! Stay tuned for updates!"
        
        # Simple template-based commentary for leaderboards
        templates = [
            "📊 Here's where we stand in the rankings!",
            "🏆 Let's check out the current leaderboard!",
            "👀 The competition is fierce! Here are the leaders!",
            "⚡ Time for a leaderboard update!",
        ]
        
        return random.choice(templates)
    
    def set_style(self, style: str):
        """
        Change commentary style
        
        Args:
            style: New commentary style
        """
        if style in self.templates:
            self.style = style
            logger.info(f"Commentary style changed to: {style}")
        else:
            logger.warning(f"Unknown style: {style}, keeping current style: {self.style}")
