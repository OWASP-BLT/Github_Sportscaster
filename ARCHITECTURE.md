# GitHub Sportscaster Architecture

## Overview

The GitHub Sportscaster is built with a modular, extensible architecture that separates concerns and makes it easy to customize and extend.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Sportscaster                       │
└─────────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼──────┐  ┌───▼────┐  ┌──────▼──────┐
        │   Web Server │  │  App   │  │    CLI      │
        │   (Flask)    │  │  Core  │  │  Interface  │
        └───────┬──────┘  └───┬────┘  └──────┬──────┘
                │             │               │
                └─────────────┼───────────────┘
                              │
                ┌─────────────▼─────────────┐
                │   Main Application Loop    │
                │    (sportscaster/app.py)   │
                └─────────────┬─────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐    ┌─────────▼─────────┐    ┌─────▼──────┐
│   GitHub     │    │    Commentary     │    │   Visual   │
│ API Monitor  │    │    Generator      │    │  Renderer  │
└───────┬──────┘    └─────────┬─────────┘    └─────┬──────┘
        │                     │                     │
        │           ┌─────────▼─────────┐          │
        │           │   Leaderboard     │          │
        │           │    Tracker        │          │
        │           └───────────────────┘          │
        │                                          │
┌───────▼──────────────────────────────────────────▼──────┐
│              Event Bus / State Manager                   │
└──────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Configuration Module (`sportscaster/config/`)

**Purpose**: Manage application settings and channel configurations

**Components**:
- `settings.py`: Pydantic models for configuration
  - `Settings`: Global application settings
  - `ChannelConfig`: Per-channel configuration

**Key Features**:
- YAML-based configuration
- Environment variable support
- Validation with Pydantic
- Multi-channel support

### 2. API Module (`sportscaster/api/`)

**Purpose**: Interface with GitHub API

**Components**:
- `github_client.py`: GitHub API wrapper
  - `GitHubClient`: Main API client class
  - `GitHubEvent`: Event data model

**Key Features**:
- Repository monitoring
- Organization tracking
- Topic/tag search
- Event parsing and normalization
- Rate limit handling

**GitHub Events Tracked**:
- ⭐ Stars
- 🍴 Forks
- 📝 Pull Requests
- 💻 Commits
- 🐛 Issues
- 🚀 Releases

### 3. Core Module (`sportscaster/core/`)

**Purpose**: Event processing and state management

**Components**:
- `monitor.py`: Event monitoring
  - `EventMonitor`: Polls GitHub for events
  - Event queue management
  - Callback system
- `leaderboard.py`: Leaderboard tracking
  - `Leaderboard`: Tracks rankings
  - Repository scores
  - User scores

**Key Features**:
- Asynchronous event polling
- Configurable poll intervals
- Event filtering
- Real-time leaderboard updates
- Multiple metric tracking

### 4. Commentary Module (`sportscaster/commentary/`)

**Purpose**: Generate sportscaster-style commentary

**Components**:
- `generator.py`: Commentary generation
  - `CommentaryGenerator`: Main generator class
  - Template-based generation
  - OpenAI integration (optional)

**Commentary Styles**:
- **Enthusiastic**: High-energy, exciting announcements
- **Professional**: Formal, informative updates
- **Dramatic**: Theatrical, storytelling approach
- **AI-Enhanced**: Context-aware, unique commentary

**Features**:
- Style switching at runtime
- Emoji integration
- Event-specific templates
- Extensible template system

### 5. Visualization Module (`sportscaster/visualization/`)

**Purpose**: Render visual frames for display

**Components**:
- `renderer.py`: Frame rendering
  - `SportscastRenderer`: Main renderer class
  - PIL-based image generation

**Display Elements**:
- Title banner
- Live commentary section
- Leaderboard panel
- Recent activity ticker
- Timestamp
- Custom styling and colors

**Features**:
- Configurable dimensions (default: 1920x1080)
- Custom fonts and colors
- Word wrapping
- Avatar support (future)
- Logo support (future)

### 6. Application Layer (`sportscaster/`)

**Purpose**: Orchestrate all components

**Components**:
- `app.py`: Main application
  - `Sportscaster`: Application class
  - Channel management
  - Event coordination
- `server.py`: Web server
  - Flask application
  - REST API endpoints
  - Live streaming

**Key Features**:
- Multi-channel support
- Asynchronous operation
- State management
- API endpoints

## Data Flow

1. **Configuration Loading**
   ```
   config.yaml → Settings → ChannelConfig
   ```

2. **Event Collection**
   ```
   GitHub API → GitHubClient → GitHubEvent → EventMonitor → Event Queue
   ```

3. **Event Processing**
   ```
   Event Queue → Callbacks → Leaderboard Update → Commentary Generation
   ```

4. **Display Update**
   ```
   Current State → Renderer → Frame Image → Web Interface
   ```

5. **API Response**
   ```
   HTTP Request → Flask Route → Current State → JSON Response
   ```

## Threading Model

- **Main Thread**: Flask web server
- **Background Thread**: Sportscaster application
- **Async Loop**: Event monitoring (asyncio)

## Extension Points

### 1. Add Custom Event Types

Edit `sportscaster/api/github_client.py`:
```python
type_mapping = {
    "WatchEvent": "star",
    "ForkEvent": "fork",
    # Add new event types here
}
```

### 2. Add Commentary Styles

Edit `sportscaster/commentary/generator.py`:
```python
def _load_templates(self):
    return {
        "enthusiastic": {...},
        "my_style": {...},  # Add new style
    }
```

### 3. Customize Visualization

Edit `sportscaster/visualization/renderer.py`:
```python
def render_frame(self, ...):
    # Customize layout, colors, fonts
```

### 4. Add New Metrics

Edit `sportscaster/core/leaderboard.py`:
```python
def process_event(self, event):
    # Add custom metric tracking
```

### 5. Integrate External Services

Create a new module:
```python
# sportscaster/integrations/discord.py
# sportscaster/integrations/slack.py
```

## Security Considerations

1. **API Tokens**: Stored in environment variables, never in code
2. **Rate Limiting**: Configurable poll intervals
3. **Input Validation**: Pydantic models validate all configuration
4. **Dependency Updates**: Regular security updates
5. **No User Input Execution**: All templates are static

## Performance Considerations

1. **Caching**: Event queue with max length
2. **Async I/O**: Non-blocking GitHub API calls
3. **Batch Processing**: Efficient API usage
4. **Configurable Limits**: Poll intervals, max events

## Testing Strategy

- **Unit Tests**: Core functionality (config, commentary, leaderboard)
- **Integration Tests**: API interactions (mocked)
- **Demo Script**: End-to-end validation
- **CI/CD**: Automated testing on push

## Deployment Options

1. **Docker**: Containerized deployment with docker-compose
2. **Direct Python**: Run directly with Python
3. **Cloud**: Deploy to any Python hosting service
4. **Kubernetes**: Scale with multiple instances

## Future Enhancements

- Video generation (moviepy integration)
- Real-time streaming (WebSocket)
- Database persistence
- User authentication
- Custom dashboards
- Mobile app integration
- Webhook support
- Analytics and insights
