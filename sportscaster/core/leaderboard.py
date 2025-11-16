"""Leaderboard tracking and management"""

import logging
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

from sportscaster.api import GitHubEvent, GitHubClient

logger = logging.getLogger(__name__)


class Leaderboard:
    """Tracks and maintains leaderboards for various metrics"""
    
    def __init__(self, client: GitHubClient, metrics: List[str] = None):
        """
        Initialize leaderboard
        
        Args:
            client: GitHub API client
            metrics: List of metrics to track (stars, forks, pull_requests, commits)
        """
        self.client = client
        self.metrics = metrics or ["stars", "forks", "pull_requests", "commits"]
        
        # Leaderboards: metric -> {entity -> count}
        self.repository_scores: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.user_scores: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        self.last_update = datetime.now()
    
    def process_event(self, event: GitHubEvent):
        """
        Process an event and update leaderboards
        
        Args:
            event: GitHub event to process
        """
        # Update user scores
        self.user_scores[event.actor][event.event_type] += 1
        
        # Update repository scores
        self.repository_scores[event.repository][event.event_type] += 1
        
        self.last_update = datetime.now()
    
    def get_top_repositories(self, metric: str = "stars", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top repositories for a metric
        
        Args:
            metric: Metric to rank by
            limit: Number of top entries to return
            
        Returns:
            List of repository rankings
        """
        if metric not in self.metrics:
            logger.warning(f"Unknown metric: {metric}")
            return []
        
        # Get scores for this metric
        scores = self.repository_scores[metric]
        
        # For stars and forks, also fetch current counts from GitHub
        if metric in ["stars", "forks"]:
            self._update_static_metrics()
        
        # Sort by score
        sorted_repos = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        results = []
        for repo_name, score in sorted_repos:
            results.append({
                "repository": repo_name,
                "score": score,
                "metric": metric,
            })
        
        return results
    
    def get_top_users(self, metric: str = "commits", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top users for a metric
        
        Args:
            metric: Metric to rank by
            limit: Number of top entries to return
            
        Returns:
            List of user rankings
        """
        if metric not in self.metrics:
            logger.warning(f"Unknown metric: {metric}")
            return []
        
        # Get scores for this metric
        scores = self.user_scores[metric]
        
        # Sort by score
        sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        results = []
        for username, score in sorted_users:
            results.append({
                "user": username,
                "score": score,
                "metric": metric,
            })
        
        return results
    
    def get_overall_rankings(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get rankings for all metrics
        
        Args:
            limit: Number of top entries per metric
            
        Returns:
            Dictionary of rankings by metric
        """
        rankings = {}
        
        for metric in self.metrics:
            rankings[f"top_repos_{metric}"] = self.get_top_repositories(metric, limit)
            rankings[f"top_users_{metric}"] = self.get_top_users(metric, limit)
        
        return rankings
    
    def _update_static_metrics(self):
        """Update static metrics like stars and forks from GitHub API"""
        # This method would fetch current counts for repositories
        # For now, we rely on event-based counting
        pass
    
    def reset(self):
        """Reset all leaderboard data"""
        self.repository_scores.clear()
        self.user_scores.clear()
        self.last_update = datetime.now()
        logger.info("Leaderboard reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get leaderboard statistics
        
        Returns:
            Dictionary of statistics
        """
        return {
            "total_repositories": len(self.repository_scores.get("commits", {})),
            "total_users": len(self.user_scores.get("commits", {})),
            "tracked_metrics": self.metrics,
            "last_update": self.last_update.isoformat(),
        }
