"""GitHub API client for monitoring repository activity"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import logging

from github import Github, GithubException
from github.Repository import Repository
from github.Organization import Organization

logger = logging.getLogger(__name__)


@dataclass
class GitHubEvent:
    """Represents a GitHub activity event"""
    
    event_type: str  # star, fork, pull_request, commit, issue, release
    repository: str  # owner/repo
    actor: str  # username
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Display data
    actor_avatar_url: Optional[str] = None
    repo_avatar_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type,
            "repository": self.repository,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "actor_avatar_url": self.actor_avatar_url,
            "repo_avatar_url": self.repo_avatar_url,
        }


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, token: str):
        """
        Initialize GitHub client
        
        Args:
            token: GitHub personal access token
        """
        self.github = Github(token)
        self.user = self.github.get_user()
        logger.info(f"Initialized GitHub client for user: {self.user.login}")
    
    def get_repository(self, repo_name: str) -> Optional[Repository]:
        """
        Get a repository by name
        
        Args:
            repo_name: Repository in format 'owner/repo'
            
        Returns:
            Repository object or None if not found
        """
        try:
            return self.github.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Error fetching repository {repo_name}: {e}")
            return None
    
    def get_organization(self, org_name: str) -> Optional[Organization]:
        """
        Get an organization by name
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization object or None if not found
        """
        try:
            return self.github.get_organization(org_name)
        except GithubException as e:
            logger.error(f"Error fetching organization {org_name}: {e}")
            return None
    
    def get_org_repositories(self, org_name: str) -> List[Repository]:
        """
        Get all repositories for an organization
        
        Args:
            org_name: Organization name
            
        Returns:
            List of repositories
        """
        org = self.get_organization(org_name)
        if not org:
            return []
        
        try:
            return list(org.get_repos())
        except GithubException as e:
            logger.error(f"Error fetching repositories for {org_name}: {e}")
            return []
    
    def get_repository_events(
        self,
        repo_name: str,
        since: Optional[datetime] = None,
        event_types: Optional[List[str]] = None
    ) -> List[GitHubEvent]:
        """
        Get recent events for a repository
        
        Args:
            repo_name: Repository in format 'owner/repo'
            since: Only return events after this timestamp
            event_types: Filter by event types
            
        Returns:
            List of GitHubEvent objects
        """
        repo = self.get_repository(repo_name)
        if not repo:
            return []
        
        events = []
        
        try:
            # Get repository events
            for event in repo.get_events():
                if since and event.created_at < since:
                    break
                
                event_obj = self._parse_event(event, repo_name)
                if event_obj and (not event_types or event_obj.event_type in event_types):
                    events.append(event_obj)
        
        except GithubException as e:
            logger.error(f"Error fetching events for {repo_name}: {e}")
        
        return events
    
    def get_stargazers_activity(
        self,
        repo_name: str,
        since: Optional[datetime] = None
    ) -> List[GitHubEvent]:
        """
        Get recent stargazer activity
        
        Args:
            repo_name: Repository in format 'owner/repo'
            since: Only return activity after this timestamp
            
        Returns:
            List of GitHubEvent objects for stars
        """
        repo = self.get_repository(repo_name)
        if not repo:
            return []
        
        events = []
        
        try:
            for stargazer in repo.get_stargazers_with_dates():
                if since and stargazer.starred_at < since:
                    break
                
                event = GitHubEvent(
                    event_type="star",
                    repository=repo_name,
                    actor=stargazer.user.login,
                    timestamp=stargazer.starred_at,
                    data={"action": "starred"},
                    actor_avatar_url=stargazer.user.avatar_url,
                    repo_avatar_url=repo.owner.avatar_url,
                )
                events.append(event)
        
        except GithubException as e:
            logger.error(f"Error fetching stargazers for {repo_name}: {e}")
        
        return events
    
    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """
        Get repository statistics
        
        Args:
            repo_name: Repository in format 'owner/repo'
            
        Returns:
            Dictionary of statistics
        """
        repo = self.get_repository(repo_name)
        if not repo:
            return {}
        
        return {
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "watchers": repo.watchers_count,
            "open_issues": repo.open_issues_count,
            "size": repo.size,
            "language": repo.language,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "description": repo.description,
        }
    
    def search_repositories_by_topic(self, topic: str, max_results: int = 30) -> List[str]:
        """
        Search repositories by topic/tag
        
        Args:
            topic: Topic to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of repository names in format 'owner/repo'
        """
        try:
            query = f"topic:{topic}"
            repositories = self.github.search_repositories(query=query, sort="stars", order="desc")
            
            repo_names = []
            for i, repo in enumerate(repositories):
                if i >= max_results:
                    break
                repo_names.append(repo.full_name)
            
            return repo_names
        
        except GithubException as e:
            logger.error(f"Error searching repositories by topic {topic}: {e}")
            return []
    
    def _parse_event(self, event: Any, repo_name: str) -> Optional[GitHubEvent]:
        """
        Parse a GitHub API event into a GitHubEvent object
        
        Args:
            event: GitHub API event object
            repo_name: Repository name
            
        Returns:
            GitHubEvent object or None
        """
        event_type = event.type
        
        # Map GitHub event types to our event types
        type_mapping = {
            "WatchEvent": "star",
            "ForkEvent": "fork",
            "PullRequestEvent": "pull_request",
            "PushEvent": "commit",
            "IssuesEvent": "issue",
            "ReleaseEvent": "release",
        }
        
        mapped_type = type_mapping.get(event_type)
        if not mapped_type:
            return None
        
        actor_avatar = event.actor.avatar_url if event.actor else None
        
        return GitHubEvent(
            event_type=mapped_type,
            repository=repo_name,
            actor=event.actor.login if event.actor else "unknown",
            timestamp=event.created_at,
            data={"raw_type": event_type},
            actor_avatar_url=actor_avatar,
        )
