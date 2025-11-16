from django.test import TestCase, Client
from django.urls import reverse
from .models import Channel, MonitoredEntity, GitHubEvent, LeaderboardEntry, Commentary
from .services import EventProcessor, GitHubService
from .ai_commentary import AICommentator
import json


class ChannelModelTest(TestCase):
    """Test Channel model"""
    
    def setUp(self):
        self.channel = Channel.objects.create(
            name="Test Channel",
            description="Test Description",
            scope="repo",
            is_active=True
        )
    
    def test_channel_creation(self):
        """Test that a channel is created correctly"""
        self.assertEqual(self.channel.name, "Test Channel")
        self.assertEqual(self.channel.scope, "repo")
        self.assertTrue(self.channel.is_active)
    
    def test_channel_str(self):
        """Test channel string representation"""
        self.assertEqual(str(self.channel), "Test Channel")


class MonitoredEntityModelTest(TestCase):
    """Test MonitoredEntity model"""
    
    def setUp(self):
        self.channel = Channel.objects.create(
            name="Test Channel",
            scope="repo"
        )
        self.entity = MonitoredEntity.objects.create(
            channel=self.channel,
            entity_type="repo",
            entity_name="owner/repo",
            is_active=True
        )
    
    def test_entity_creation(self):
        """Test that an entity is created correctly"""
        self.assertEqual(self.entity.entity_name, "owner/repo")
        self.assertEqual(self.entity.channel, self.channel)
        self.assertTrue(self.entity.is_active)


class GitHubEventModelTest(TestCase):
    """Test GitHubEvent model"""
    
    def setUp(self):
        self.channel = Channel.objects.create(name="Test Channel", scope="repo")
        self.event = GitHubEvent.objects.create(
            channel=self.channel,
            event_type="star",
            repository="owner/repo",
            actor="testuser",
            event_data={"test": "data"}
        )
    
    def test_event_creation(self):
        """Test that an event is created correctly"""
        self.assertEqual(self.event.event_type, "star")
        self.assertEqual(self.event.repository, "owner/repo")
        self.assertEqual(self.event.actor, "testuser")
        self.assertFalse(self.event.processed)


class EventProcessorTest(TestCase):
    """Test EventProcessor service"""
    
    def test_process_watch_event(self):
        """Test processing of a WatchEvent (star)"""
        raw_event = {
            'type': 'WatchEvent',
            'repo': {'name': 'owner/repo'},
            'actor': {'login': 'testuser', 'avatar_url': 'http://example.com/avatar.jpg'},
            'created_at': '2023-01-01T00:00:00Z',
            'payload': {}
        }
        
        processor = EventProcessor()
        processed = processor.process_event(raw_event)
        
        self.assertIsNotNone(processed)
        self.assertEqual(processed['event_type'], 'star')
        self.assertEqual(processed['repository'], 'owner/repo')
        self.assertEqual(processed['actor'], 'testuser')
    
    def test_process_fork_event(self):
        """Test processing of a ForkEvent"""
        raw_event = {
            'type': 'ForkEvent',
            'repo': {'name': 'owner/repo'},
            'actor': {'login': 'testuser', 'avatar_url': 'http://example.com/avatar.jpg'},
            'created_at': '2023-01-01T00:00:00Z',
            'payload': {}
        }
        
        processor = EventProcessor()
        processed = processor.process_event(raw_event)
        
        self.assertEqual(processed['event_type'], 'fork')
    
    def test_get_event_description(self):
        """Test event description generation"""
        event = {
            'event_type': 'star',
            'repository': 'owner/repo',
            'actor': 'testuser'
        }
        
        processor = EventProcessor()
        description = processor.get_event_description(event)
        
        self.assertIn('testuser', description)
        self.assertIn('starred', description)
        self.assertIn('owner/repo', description)


class AICommentatorTest(TestCase):
    """Test AI Commentary generation"""
    
    def test_generate_commentary_star(self):
        """Test commentary generation for star event"""
        event = {
            'event_type': 'star',
            'repository': 'owner/repo',
            'actor': 'testuser'
        }
        
        commentator = AICommentator()
        commentary = commentator.generate_commentary(event)
        
        self.assertIsNotNone(commentary)
        self.assertIsInstance(commentary, str)
        self.assertTrue(len(commentary) > 0)
    
    def test_generate_commentary_pull_request(self):
        """Test commentary generation for pull request event"""
        event = {
            'event_type': 'pull_request',
            'repository': 'owner/repo',
            'actor': 'testuser'
        }
        
        commentator = AICommentator()
        commentary = commentator.generate_commentary(event)
        
        self.assertIsNotNone(commentary)
        self.assertTrue(len(commentary) > 0)


class ViewsTest(TestCase):
    """Test views"""
    
    def setUp(self):
        self.client = Client()
        self.channel = Channel.objects.create(
            name="Test Channel",
            description="Test Description",
            scope="repo",
            is_active=True
        )
    
    def test_index_view(self):
        """Test index view"""
        response = self.client.get(reverse('sportscaster:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GitHub Sportscaster")
    
    def test_channel_view(self):
        """Test channel view"""
        response = self.client.get(reverse('sportscaster:channel', args=[self.channel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.channel.name)
    
    def test_api_channels(self):
        """Test API channels endpoint"""
        response = self.client.get(reverse('sportscaster:api_channels'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Channel")
    
    def test_api_channel_events(self):
        """Test API channel events endpoint"""
        # Create test event
        GitHubEvent.objects.create(
            channel=self.channel,
            event_type="star",
            repository="owner/repo",
            actor="testuser",
            event_data={"test": "data"}
        )
        
        response = self.client.get(
            reverse('sportscaster:api_channel_events', args=[self.channel.id])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event_type'], "star")
    
    def test_api_leaderboard(self):
        """Test API leaderboard endpoint"""
        # Create test leaderboard entry
        LeaderboardEntry.objects.create(
            channel=self.channel,
            repository="owner/repo",
            stars=100,
            forks=50,
            rank=1
        )
        
        response = self.client.get(
            reverse('sportscaster:api_leaderboard', args=[self.channel.id])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['stars'], 100)


class LeaderboardTest(TestCase):
    """Test leaderboard functionality"""
    
    def setUp(self):
        self.channel = Channel.objects.create(name="Test Channel", scope="repo")
    
    def test_leaderboard_ordering(self):
        """Test that leaderboard entries are ordered correctly"""
        LeaderboardEntry.objects.create(
            channel=self.channel,
            repository="repo1",
            stars=100,
            forks=50
        )
        LeaderboardEntry.objects.create(
            channel=self.channel,
            repository="repo2",
            stars=200,
            forks=75
        )
        
        entries = LeaderboardEntry.objects.filter(channel=self.channel).order_by('-stars')
        self.assertEqual(entries[0].repository, "repo2")
        self.assertEqual(entries[1].repository, "repo1")
