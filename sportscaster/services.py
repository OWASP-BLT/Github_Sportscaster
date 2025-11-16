"""
Services for GitHub API integration and event monitoring
"""
import requests
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self):
        self.base_url = settings.GITHUB_API_BASE_URL
        self.token = settings.GITHUB_TOKEN
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def get_repository_events(self, owner: str, repo: str, per_page: int = 30) -> List[Dict]:
        """Fetch events for a specific repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/events"
        params = {'per_page': per_page}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching repository events: {e}")
            return []
    
    def get_repository_stats(self, owner: str, repo: str) -> Dict:
        """Fetch repository statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'name': data.get('full_name', ''),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'watchers': data.get('watchers_count', 0),
                'open_issues': data.get('open_issues_count', 0),
                'description': data.get('description', ''),
                'owner_avatar': data.get('owner', {}).get('avatar_url', ''),
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching repository stats: {e}")
            return {}
    
    def get_organization_repos(self, org: str, per_page: int = 30) -> List[Dict]:
        """Fetch repositories for an organization"""
        url = f"{self.base_url}/orgs/{org}/repos"
        params = {'per_page': per_page, 'sort': 'updated'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching organization repos: {e}")
            return []
    
    def search_repositories(self, query: str, sort: str = 'stars', per_page: int = 30) -> List[Dict]:
        """Search repositories on GitHub"""
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': query,
            'sort': sort,
            'per_page': per_page,
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.RequestException as e:
            logger.error(f"Error searching repositories: {e}")
            return []
    
    def get_public_events(self, per_page: int = 30) -> List[Dict]:
        """Fetch public events from all of GitHub"""
        url = f"{self.base_url}/events"
        params = {'per_page': per_page}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching public events: {e}")
            return []


class EventProcessor:
    """Process and normalize GitHub events"""
    
    @staticmethod
    def process_event(event: Dict) -> Optional[Dict]:
        """Process a raw GitHub event into normalized format"""
        event_type_map = {
            'WatchEvent': 'star',
            'ForkEvent': 'fork',
            'PullRequestEvent': 'pull_request',
            'PushEvent': 'commit',
            'ReleaseEvent': 'release',
            'IssuesEvent': 'issue',
        }
        
        raw_type = event.get('type', '')
        event_type = event_type_map.get(raw_type)
        
        if not event_type:
            return None
        
        repo = event.get('repo', {}).get('name', '')
        actor = event.get('actor', {})
        
        processed = {
            'event_type': event_type,
            'repository': repo,
            'actor': actor.get('login', ''),
            'actor_avatar': actor.get('avatar_url', ''),
            'timestamp': event.get('created_at', ''),
            'event_data': event.get('payload', {}),
        }
        
        return processed
    
    @staticmethod
    def get_event_description(event: Dict) -> str:
        """Generate a human-readable description of an event"""
        event_type = event.get('event_type', '')
        repo = event.get('repository', '')
        actor = event.get('actor', 'Someone')
        
        descriptions = {
            'star': f"{actor} starred {repo}",
            'fork': f"{actor} forked {repo}",
            'pull_request': f"{actor} opened a pull request on {repo}",
            'commit': f"{actor} pushed commits to {repo}",
            'release': f"{actor} released a new version of {repo}",
            'issue': f"{actor} opened an issue on {repo}",
        }
        
        return descriptions.get(event_type, f"{actor} performed an action on {repo}")
