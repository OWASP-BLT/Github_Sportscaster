# GitHub Sportscaster - Architecture Documentation

## Overview

The GitHub Sportscaster is a real-time web application that monitors GitHub activity and presents it as an engaging sports-style broadcast with AI-powered commentary.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ HTML/CSS/JS│  │  WebSocket   │  │  REST API Calls  │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────┬──────────────────────┬───────────────┘
                       │                       │
                       │ Real-time Events      │ HTTP Requests
                       │                       │
┌──────────────────────┴───────────────────────┴───────────────┐
│                    Django Application                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ASGI Application (Daphne)              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Views &    │  │  WebSocket   │  │ Management   │      │
│  │  API Endpoints│  │  Consumers   │  │  Commands    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Business Logic Layer                  │   │
│  │  ┌────────────┐  ┌───────────┐  ┌───────────────┐  │   │
│  │  │  GitHub    │  │   Event   │  │      AI       │  │   │
│  │  │  Service   │  │ Processor │  │  Commentator  │  │   │
│  │  └────────────┘  └───────────┘  └───────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Data Models                        │   │
│  │  Channel | MonitoredEntity | GitHubEvent |           │   │
│  │  LeaderboardEntry | Commentary                       │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ↓
        ┌───────────────────────────┐
        │     Database (SQLite)     │
        │     (PostgreSQL in prod)  │
        └───────────────────────────┘

External Services:
┌──────────────┐         ┌──────────────┐
│   GitHub API │         │  OpenAI API  │
└──────────────┘         └──────────────┘
```

## Core Components

### 1. Django Application Layer

#### Models (`sportscaster/models.py`)

**Channel**
- Represents a monitoring channel (e.g., "Hot Python Projects")
- Configures scope: all GitHub, org, repo, tag, or custom list
- Manages active/inactive state

**MonitoredEntity**
- Links specific GitHub entities to channels
- Stores entity type (org/repo/tag) and name
- Enables/disables monitoring per entity

**GitHubEvent**
- Records captured GitHub events
- Stores event type, repository, actor, and raw data
- Tracks processing status
- Links to channels for filtering

**LeaderboardEntry**
- Maintains repository rankings within channels
- Tracks stars, forks, PRs, and commits
- Auto-updates rank based on metrics

**Commentary**
- Stores AI-generated commentary for events
- One-to-one relationship with GitHubEvent
- Includes generation timestamp

#### Views & API (`sportscaster/views.py`)

**Web Views**
- `index`: Homepage displaying available channels
- `channel_view`: Individual channel broadcast page

**API Endpoints**
- `api_channels`: GET list of active channels
- `api_channel_events`: GET events for specific channel
- `api_leaderboard`: GET leaderboard for specific channel
- `api_test_commentary`: POST to test AI commentary generation

### 2. Real-time Communication Layer

#### WebSocket Consumers (`sportscaster/consumers.py`)

**SportscasterConsumer**
- Handles WebSocket connections per channel
- Manages room groups for broadcasting
- Processes incoming messages (ping/pong)
- Distributes events, leaderboard updates, and commentary

**Message Types**
- `event_message`: New GitHub event detected
- `leaderboard_update`: Leaderboard changes
- `commentary_message`: AI commentary broadcast

#### Routing (`sportscaster/routing.py`)

Maps WebSocket URLs to consumers:
```
ws://host/ws/sportscaster/<channel_id>/
```

### 3. Business Logic Layer

#### GitHub Service (`sportscaster/services.py`)

**GitHubService Class**
- Interfaces with GitHub REST API
- Handles authentication with token
- Methods:
  - `get_repository_events`: Fetch events for repo
  - `get_repository_stats`: Get stars, forks, etc.
  - `get_organization_repos`: List org repositories
  - `search_repositories`: Search GitHub repos
  - `get_public_events`: Fetch public GitHub events

**EventProcessor Class**
- Normalizes raw GitHub events
- Maps GitHub event types to internal types:
  - WatchEvent → star
  - ForkEvent → fork
  - PullRequestEvent → pull_request
  - PushEvent → commit
  - ReleaseEvent → release
  - IssuesEvent → issue
- Generates human-readable descriptions

#### AI Commentary (`sportscaster/ai_commentary.py`)

**AICommentator Class**
- Generates sports-style commentary
- Two modes:
  1. Template-based (default/fallback)
  2. OpenAI API (when configured)
- Context-aware with leaderboard integration
- Multiple commentary templates per event type

### 4. Background Processing

#### Management Commands

**monitor_github** (`sportscaster/management/commands/monitor_github.py`)
- Background service for continuous monitoring
- Polls GitHub API at configurable intervals
- Processes events per channel
- Updates leaderboard metrics
- Broadcasts via WebSocket using channel layers
- Supports:
  - Custom polling intervals
  - Single channel monitoring
  - Rate limiting awareness

**setup_demo** (`sportscaster/management/commands/setup_demo.py`)
- Populates database with demo channels
- Creates sample monitored entities
- Quick setup for testing

### 5. Frontend Layer

#### Templates

**base.html**
- Common layout and styling
- Gradient background theme
- Responsive design

**index.html**
- Channel selection grid
- Displays all active channels
- Click-to-navigate to channel view

**channel.html**
- Live sportscaster interface
- Features:
  - WebSocket connection status
  - Animated sportscaster bot
  - Real-time commentary display
  - Live leaderboard
  - Scrolling events feed
  - Auto-reconnection logic

#### Frontend JavaScript

**WebSocket Management**
- Automatic connection on page load
- Reconnection with exponential backoff
- Ping/pong keepalive
- Message routing to UI components

**Dynamic UI Updates**
- Real-time event insertion
- Animated leaderboard updates
- Commentary text transitions
- Connection status indicators

## Data Flow

### Event Monitoring Flow

```
1. monitor_github command starts
2. Loop every N seconds:
   a. Query active channels from database
   b. For each channel:
      - Get monitored entities
      - For each entity:
        * Call GitHub API for events
        * Process raw events
        * Check for duplicates
        * Store new events in database
        * Generate AI commentary
        * Broadcast via WebSocket
      - Update leaderboard
      - Broadcast leaderboard via WebSocket
3. Sleep and repeat
```

### Real-time Broadcast Flow

```
1. New event detected by monitor
2. Event saved to database
3. Commentary generated
4. Message sent to channel layer
5. Channel layer broadcasts to all connected clients in room
6. WebSocket consumer receives message
7. Consumer sends to client browser
8. JavaScript updates UI
```

### User Interaction Flow

```
1. User opens homepage
2. Django renders list of channels
3. User clicks channel
4. Channel page loads
5. JavaScript establishes WebSocket connection
6. Initial data loaded via REST API
7. Real-time updates received via WebSocket
8. UI updates automatically
```

## Scalability Considerations

### Current Implementation (Development)

- **Database**: SQLite (single-file, simple)
- **Channel Layer**: In-memory (single process)
- **Web Server**: Django development server

### Production Recommendations

- **Database**: PostgreSQL or MySQL
  - Better concurrency
  - Advanced indexing
  - Replication support

- **Channel Layer**: Redis
  - Distributed WebSocket support
  - Multiple server instances
  - Horizontal scaling

- **Web Server**: Daphne or Uvicorn
  - Production ASGI server
  - Better performance
  - More concurrent connections

- **Process Management**: 
  - Systemd for service management
  - Docker for containerization
  - Kubernetes for orchestration

- **Load Balancing**:
  - Nginx or HAProxy
  - SSL termination
  - WebSocket proxy support

### Performance Optimization

1. **Caching**
   - Redis for API response caching
   - Cache repository stats
   - Rate limit API calls

2. **Database Optimization**
   - Index on timestamp + channel
   - Index on processed status
   - Regular cleanup of old events

3. **API Rate Limiting**
   - GitHub: 5000 requests/hour (authenticated)
   - Implement exponential backoff
   - Cache frequent queries

4. **WebSocket Optimization**
   - Message batching
   - Compression
   - Connection pooling

## Security Considerations

1. **API Keys**
   - Store in environment variables
   - Never commit to repository
   - Rotate regularly

2. **WebSocket Security**
   - AllowedHostsOriginValidator
   - AuthMiddleware for authenticated channels
   - HTTPS in production (WSS)

3. **Database**
   - Parameterized queries (Django ORM)
   - Regular backups
   - Access controls

4. **Input Validation**
   - Validate GitHub event data
   - Sanitize user inputs
   - Rate limiting on API endpoints

## Extension Points

### Adding New Event Types

1. Update `EventProcessor.process_event()` mapping
2. Add template in `AICommentator._generate_template_commentary()`
3. Update frontend display logic

### Adding New Data Sources

1. Create new service class (similar to `GitHubService`)
2. Implement event normalization
3. Update monitoring command
4. Add new entity types to models

### Customizing UI

1. Modify templates in `sportscaster/templates/`
2. Add custom CSS in `<style>` blocks
3. Extend JavaScript for new features

### AI Integration

1. Implement `_call_openai_api()` in `AICommentator`
2. Configure API key in environment
3. Customize system prompt for desired style
4. Add error handling and fallback

## Testing Strategy

### Unit Tests

- Model creation and validation
- Event processing logic
- Commentary generation
- Service API calls (mocked)

### Integration Tests

- API endpoint responses
- WebSocket message flow
- Database queries
- End-to-end event processing

### Manual Testing

- UI rendering across browsers
- WebSocket connection stability
- Real-time update latency
- Error handling and recovery

## Monitoring & Logging

### Application Logs

- Django logging framework
- Service-level logs in `services.py`
- Command logs in management commands
- WebSocket connection logs

### Metrics to Track

- Events processed per minute
- API call count and errors
- WebSocket connections active
- Commentary generation time
- Database query performance

### Health Checks

- WebSocket connectivity
- GitHub API availability
- Database connection
- Channel layer status

## Future Enhancements

1. **User Authentication**
   - Personal channels
   - Custom repository lists
   - Notification preferences

2. **Advanced Analytics**
   - Trend detection
   - Comparative analysis
   - Historical charts

3. **Enhanced AI**
   - Voice synthesis
   - Video generation
   - Multi-language support

4. **Social Features**
   - Share channels
   - Collaborative curation
   - Comments and reactions

5. **Mobile App**
   - Native iOS/Android
   - Push notifications
   - Offline mode
