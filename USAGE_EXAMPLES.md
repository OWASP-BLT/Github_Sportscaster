# GitHub Sportscaster - Usage Examples

This guide provides practical examples for different use cases of the GitHub Sportscaster.

## Table of Contents

1. [Monitoring Popular Frameworks](#monitoring-popular-frameworks)
2. [Tracking Organization Activity](#tracking-organization-activity)
3. [Hackathon Event Coverage](#hackathon-event-coverage)
4. [Personal Project Dashboard](#personal-project-dashboard)
5. [Technology Trend Comparison](#technology-trend-comparison)
6. [Custom Event Filtering](#custom-event-filtering)
7. [Integration Examples](#integration-examples)

---

## Monitoring Popular Frameworks

**Use Case**: Track activity across popular web frameworks to see which is gaining the most traction.

### Setup

1. Create a channel via admin panel:
   - **Name**: "Web Framework Battle"
   - **Description**: "Real-time competition between top web frameworks"
   - **Scope**: Custom

2. Add monitored entities:
   ```
   facebook/react
   vuejs/vue
   angular/angular
   sveltejs/svelte
   vercel/next.js
   ```

3. Start monitoring:
   ```bash
   python manage.py monitor_github --channel-id 1
   ```

### Expected Output

The sportscaster will announce:
- "⭐ What a move! John Doe just gave facebook/react a star!"
- "🍴 Fork alert! Jane Smith forks vuejs/vue!"
- "📝 Pull request incoming! Developer contributes to angular/angular!"

The leaderboard shows real-time rankings by stars and forks.

---

## Tracking Organization Activity

**Use Case**: Monitor all activity within a specific GitHub organization.

### Setup

1. Create a channel:
   - **Name**: "Mozilla Activity"
   - **Description**: "Live tracking of Mozilla organization"
   - **Scope**: Organization

2. Add the organization:
   ```
   mozilla/firefox
   mozilla/rust
   mozilla/pdf.js
   mozilla/servo
   ```

3. Customize monitoring interval for high activity:
   ```bash
   python manage.py monitor_github --channel-id 2 --interval 30
   ```

### Use Cases

- **Open Source Transparency**: Show community how active development is
- **Team Dashboard**: Display on office screens
- **Project Management**: Track when releases happen

---

## Hackathon Event Coverage

**Use Case**: Create excitement during a hackathon by broadcasting all submission activity.

### Setup

1. Create a channel before the hackathon:
   - **Name**: "HackNight 2024"
   - **Description**: "Live coverage of HackNight hackathon submissions"
   - **Scope**: Custom

2. Add hackathon repositories as teams create them:
   ```python
   # Can be automated via API
   from sportscaster.models import Channel, MonitoredEntity
   
   channel = Channel.objects.get(name="HackNight 2024")
   
   # Add each team's repo as they're created
   MonitoredEntity.objects.create(
       channel=channel,
       entity_type='repo',
       entity_name='hacknight/team-awesome',
       is_active=True
   )
   ```

3. Display on projector during event

### Features

- Real-time commit counts per team
- Pull request activity visualization
- Live commentary: "🔨 Team Awesome pushes their final commits!"
- Leaderboard showing most active teams

---

## Personal Project Dashboard

**Use Case**: Monitor your own projects and see all activity in one place.

### Setup

1. Create a personal channel:
   - **Name**: "My Projects"
   - **Description**: "Activity across all my repositories"
   - **Scope**: Custom

2. Add your repositories:
   ```
   yourusername/project1
   yourusername/project2
   yourusername/project3
   yourorg/company-project
   ```

### Benefits

- See who's contributing to your projects
- Track stars and forks
- Get notified of issues and PRs
- Monitor community engagement

---

## Technology Trend Comparison

**Use Case**: Compare adoption trends between competing technologies.

### Example: Python vs Go vs Rust

1. Create channel "Language Wars 2024"

2. Add representative projects:
   ```
   # Python
   python/cpython
   django/django
   psf/requests
   
   # Go
   golang/go
   kubernetes/kubernetes
   docker/compose
   
   # Rust
   rust-lang/rust
   actix/actix-web
   tokio-rs/tokio
   ```

3. Monitor over time to see trends

### Insights

- Which language has more active development?
- Which community is more engaged?
- What's the star/fork ratio?
- How many commits per day?

---

## Custom Event Filtering

**Use Case**: Only show specific types of events.

### Filter for Releases Only

Modify `sportscaster/management/commands/monitor_github.py`:

```python
# Add filtering in process_entity method
if event_type not in ['release']:
    continue
```

### Filter for Major Stars (multiples of 100)

```python
# In AI commentary generation
if event_type == 'star':
    stats = github_service.get_repository_stats(owner, repo)
    if stats['stars'] % 100 == 0:
        commentary = f"🎉 MILESTONE! {repo} just hit {stats['stars']} stars!"
```

---

## Integration Examples

### 1. Slack Integration

Post major events to Slack:

```python
# In sportscaster/services.py
import requests

def post_to_slack(event, commentary):
    webhook_url = settings.SLACK_WEBHOOK_URL
    message = {
        "text": commentary,
        "attachments": [{
            "color": "good",
            "fields": [
                {"title": "Repository", "value": event['repository'], "short": True},
                {"title": "Actor", "value": event['actor'], "short": True}
            ]
        }]
    }
    requests.post(webhook_url, json=message)
```

### 2. Discord Bot

```python
# In monitor_github.py
from discord_webhook import DiscordWebhook

def post_to_discord(event, commentary):
    webhook = DiscordWebhook(
        url=settings.DISCORD_WEBHOOK_URL,
        content=f"**{commentary}**\n`{event['repository']}`"
    )
    webhook.execute()
```

### 3. Twitter Bot

```python
# Post major milestones to Twitter
import tweepy

def tweet_milestone(event, commentary):
    if should_tweet(event):  # e.g., every 1000 stars
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        api.update_status(commentary)
```

### 4. Email Digest

Create a daily summary:

```python
# New management command: send_daily_digest.py
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

def send_digest():
    yesterday = timezone.now() - timedelta(days=1)
    events = GitHubEvent.objects.filter(timestamp__gte=yesterday)
    
    # Generate summary
    summary = generate_daily_summary(events)
    
    send_mail(
        'GitHub Sportscaster Daily Digest',
        summary,
        'sportscaster@example.com',
        ['your-email@example.com'],
    )
```

### 5. Custom Dashboard Widget

Embed in your website:

```html
<iframe 
    src="http://sportscaster.example.com/channel/1/"
    width="800" 
    height="600"
    frameborder="0">
</iframe>
```

### 6. REST API Client

Fetch data programmatically:

```python
import requests

# Get channel list
channels = requests.get('http://localhost:8000/api/channels/').json()

# Get events for channel 1
events = requests.get('http://localhost:8000/api/channel/1/events/?limit=20').json()

# Get leaderboard
leaderboard = requests.get('http://localhost:8000/api/channel/1/leaderboard/').json()

# Test commentary generation
commentary = requests.post(
    'http://localhost:8000/api/test-commentary/',
    json={
        'event_type': 'star',
        'repository': 'owner/repo',
        'actor': 'username'
    }
).json()
```

### 7. Mobile App Integration

```javascript
// React Native WebSocket example
import React, { useEffect, useState } from 'react';
import { WebSocket } from 'react-native';

const SportscasterStream = ({ channelId }) => {
    const [events, setEvents] = useState([]);
    
    useEffect(() => {
        const ws = new WebSocket(`ws://sportscaster.example.com/ws/sportscaster/${channelId}/`);
        
        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'event') {
                setEvents(prev => [data, ...prev].slice(0, 50));
            }
        };
        
        return () => ws.close();
    }, [channelId]);
    
    return (
        <FlatList
            data={events}
            renderItem={({ item }) => <EventCard event={item} />}
        />
    );
};
```

---

## Advanced Configurations

### High-Frequency Monitoring

For very active repositories:

```bash
# Poll every 15 seconds
python manage.py monitor_github --interval 15
```

**Note**: Be aware of GitHub API rate limits (5000/hour with token).

### Multi-Channel Setup

Run separate processes for different channels:

```bash
# Terminal 1: Monitor Python projects
python manage.py monitor_github --channel-id 1 --interval 60

# Terminal 2: Monitor JavaScript projects  
python manage.py monitor_github --channel-id 2 --interval 60

# Terminal 3: Monitor all other channels
python manage.py monitor_github --interval 120
```

### Production Deployment with systemd

Create `/etc/systemd/system/sportscaster-monitor@.service`:

```ini
[Unit]
Description=GitHub Sportscaster Monitor for Channel %i
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sportscaster
Environment="PATH=/var/www/sportscaster/venv/bin"
ExecStart=/var/www/sportscaster/venv/bin/python manage.py monitor_github --channel-id %i
Restart=always

[Install]
WantedBy=multi-user.target
```

Start services:
```bash
sudo systemctl enable sportscaster-monitor@1
sudo systemctl start sportscaster-monitor@1
```

---

## Tips and Best Practices

### 1. Rate Limiting

- Use GitHub token for 5000 requests/hour
- Increase polling interval for less active repos
- Cache repository stats

### 2. Performance

- Limit events to last 100 per channel
- Use database indexes effectively
- Clean old events periodically

### 3. User Experience

- Show connection status clearly
- Implement reconnection logic
- Add loading states
- Handle errors gracefully

### 4. Customization

- Modify templates for your brand
- Add custom CSS themes
- Customize commentary style
- Add sound effects

### 5. Monitoring

- Log all API calls
- Track WebSocket connection count
- Monitor database size
- Alert on failures

---

## Troubleshooting Common Issues

### Events Not Appearing

1. Check if monitor command is running
2. Verify GitHub token is valid
3. Check monitored entities are active
4. Look for API rate limit errors

### WebSocket Disconnects

1. Implement reconnection (already included)
2. Use Redis in production for stability
3. Check firewall/proxy WebSocket support
4. Verify CORS settings

### Slow Performance

1. Reduce polling frequency
2. Limit events per query
3. Add database indexes
4. Use Redis for caching

---

## Community Contributions

Share your use cases and configurations:

1. Fork the repository
2. Add your example to this file
3. Submit a pull request
4. Help others learn from your setup!

---

## Support

For questions or issues with these examples:
- Open an issue on GitHub
- Check the [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review [SETUP.md](SETUP.md) for configuration help
