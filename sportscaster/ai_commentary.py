"""
AI-powered commentary generation for GitHub events
"""
from django.conf import settings
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Mock implementation for AI commentary
# In production, this would use the OpenAI API with o3-mini-high model


class AICommentator:
    """Generate sports-style commentary for GitHub events"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    def generate_commentary(self, event: Dict, leaderboard_context: Optional[Dict] = None) -> str:
        """
        Generate engaging sports-style commentary for a GitHub event
        
        Args:
            event: Processed event data
            leaderboard_context: Optional context about repository rankings
        
        Returns:
            Generated commentary text
        """
        # For now, use template-based commentary
        # In production, this would call OpenAI API
        return self._generate_template_commentary(event, leaderboard_context)
    
    def _generate_template_commentary(self, event: Dict, leaderboard_context: Optional[Dict] = None) -> str:
        """Generate commentary using templates (fallback/mock)"""
        event_type = event.get('event_type', '')
        repo = event.get('repository', '')
        actor = event.get('actor', 'A developer')
        
        templates = {
            'star': [
                f"🌟 And there it is! {actor} just gave {repo} a star! The crowd goes wild!",
                f"⭐ What a move by {actor}! {repo} adds another star to their collection!",
                f"🎯 {actor} shows their appreciation with a star for {repo}! The momentum is building!",
                f"✨ Star power! {actor} just boosted {repo}'s stellar count!",
            ],
            'fork': [
                f"🍴 Fork alert! {actor} has forked {repo}! Someone's building something interesting!",
                f"🔱 Major development! {actor} forks {repo} - a new journey begins!",
                f"🎪 {actor} splits off from {repo}! Innovation in action, folks!",
                f"⚡ Fork in the road! {actor} takes {repo} in a new direction!",
            ],
            'pull_request': [
                f"📝 Pull request incoming! {actor} is contributing to {repo}! Teamwork makes the dream work!",
                f"🚀 {actor} steps up with a pull request for {repo}! Collaboration at its finest!",
                f"💪 Bold move! {actor} submits a pull request to improve {repo}!",
                f"🎯 {actor} takes the shot with a pull request on {repo}! Let's see if it scores!",
            ],
            'commit': [
                f"💻 Commit! {actor} pushes code to {repo}! The build is live!",
                f"⚡ Lightning fast! {actor} commits changes to {repo}! Progress never stops!",
                f"🔨 Building the future! {actor} commits to {repo}! Every line counts!",
                f"🎪 {actor} delivers! Fresh commits landing on {repo}!",
            ],
            'release': [
                f"🎉 RELEASE TIME! {actor} just dropped a new version of {repo}! History in the making!",
                f"🚀 Launch detected! {actor} releases {repo}! New features incoming!",
                f"📦 Package delivered! {actor} ships a fresh release of {repo}!",
                f"🎊 It's official! {actor} announces a new release for {repo}! Celebration time!",
            ],
            'issue': [
                f"🔍 Issue spotted! {actor} opens a ticket on {repo}! The team is on it!",
                f"📋 {actor} raises concerns about {repo}! Transparency in action!",
                f"🎯 {actor} identifies an opportunity with an issue on {repo}! Every bug is a chance to improve!",
                f"⚠️ {actor} files an issue on {repo}! The community rallies!",
            ],
        }
        
        import random
        commentary_list = templates.get(event_type, [
            f"📊 Activity detected! {actor} interacts with {repo}!"
        ])
        
        commentary = random.choice(commentary_list)
        
        # Add leaderboard context if available
        if leaderboard_context:
            rank_info = leaderboard_context.get('rank_change')
            if rank_info:
                commentary += f" {rank_info}"
        
        return commentary
    
    def _call_openai_api(self, event: Dict, leaderboard_context: Optional[Dict] = None) -> str:
        """
        Call OpenAI API for commentary generation
        This is a placeholder for production implementation
        """
        # In production, implement actual OpenAI API call here
        # Example:
        # import openai
        # openai.api_key = self.api_key
        # 
        # prompt = self._build_prompt(event, leaderboard_context)
        # response = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=[
        #         {"role": "system", "content": "You are an enthusiastic sports announcer for GitHub events."},
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        # return response.choices[0].message.content
        
        return self._generate_template_commentary(event, leaderboard_context)
    
    def _build_prompt(self, event: Dict, leaderboard_context: Optional[Dict] = None) -> str:
        """Build a prompt for the AI model"""
        event_type = event.get('event_type', '')
        repo = event.get('repository', '')
        actor = event.get('actor', '')
        
        prompt = f"""Generate exciting sports-style commentary for this GitHub event:
        
Event Type: {event_type}
Repository: {repo}
Actor: {actor}

Guidelines:
- Use energetic, sports announcer style language
- Keep it short and punchy (1-2 sentences)
- Include relevant emojis
- Make it engaging and fun
- Reference the specific action and repository
"""
        
        if leaderboard_context:
            prompt += f"\nLeaderboard Context: {leaderboard_context}"
        
        return prompt
