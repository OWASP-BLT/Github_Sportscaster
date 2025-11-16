# GitHub Sportscaster 🎙️

An AI-powered animated announcer bot that monitors GitHub activity across repositories, providing dynamic video streams with live play-by-play announcements and real-time leaderboards.

## Features

### 🔍 Monitoring & Configuration
- **Flexible Scope**: Monitor entire GitHub, specific organizations, single or multiple repositories, tags, or curated lists
- **Event Types**: Captures key actions including:
  - Star counts and changes
  - New pull requests
  - Commits and releases
  - Forks and other engagement metrics
  - Issues and special events

### 🎬 Live Video Representation
- Dynamic, video-based UI featuring an AI bot sportscaster
- Real-time event announcements with engaging commentary
- Project logos and key metrics display
- User avatars alongside actions
- Live commentary and visual effects

### 📊 Leaderboard & Analytics
- Real-time leaderboard showing ranking changes
- Visual transitions and animations for significant changes
- Tracks stars, forks, pull requests, and commits

### 📺 User Channels & Curation
- Users can create channels for specific projects or organizations
- Multiple channels for different themes or events
- Easy channel switching and management

### 🤖 AI Commentary
- Sports-style commentary powered by AI (o3-mini-high model)
- Engaging, dynamic play-by-play language
- Context-aware announcements based on leaderboard changes

### 🔧 Extensibility
- Modular architecture for adding new event types
- Designed to integrate with other online event streams
- Easy to extend for hackathons and coding competitions

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Real-time Communication**: Django Channels with WebSocket support
- **Frontend**: HTML5, JavaScript, CSS3 with real-time updates
- **Data Integration**: GitHub API via PyGithub
- **AI Integration**: OpenAI API (o3-mini-high model)
- **Database**: SQLite (development), PostgreSQL recommended for production

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Redis (for production WebSocket support)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/OWASP-BLT/Github_Sportscaster.git
cd Github_Sportscaster
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token
- `OPENAI_API_KEY`: Your OpenAI API key (for AI commentary)
- `SECRET_KEY`: Django secret key
- Other optional settings

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Create a superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

## Usage

### Starting the Application

1. **Start the Django development server**
```bash
python manage.py runserver
```

2. **In a separate terminal, start the GitHub monitoring service**
```bash
python manage.py monitor_github
```

3. **Access the application**
- Open your browser to `http://localhost:8000`
- Admin panel: `http://localhost:8000/admin`

### Creating a Channel

1. Log in to the admin panel
2. Navigate to "Channels" and click "Add Channel"
3. Configure the channel:
   - Name: Give your channel a descriptive name
   - Description: Describe what the channel monitors
   - Scope: Choose the monitoring scope (all, org, repo, tag, custom)
   - Active: Check to enable monitoring

4. Add monitored entities:
   - Navigate to "Monitored Entities"
   - Add repositories (format: `owner/repo`)
   - Link to the channel you created

### Monitoring Options

The `monitor_github` command supports several options:

```bash
# Monitor with custom interval (default: 60 seconds)
python manage.py monitor_github --interval 120

# Monitor specific channel only
python manage.py monitor_github --channel-id 1
```

## API Endpoints

### Channels
- `GET /api/channels/` - List all active channels
- `GET /api/channel/<id>/events/` - Get events for a channel
- `GET /api/channel/<id>/leaderboard/` - Get leaderboard for a channel

### Testing
- `POST /api/test-commentary/` - Test AI commentary generation

## WebSocket Communication

Connect to live updates via WebSocket:

```javascript
ws://localhost:8000/ws/sportscaster/<channel_id>/
```

### Message Types
- `event` - New GitHub event detected
- `leaderboard` - Leaderboard update
- `commentary` - AI-generated commentary

## Development

### Running Tests
```bash
python manage.py test sportscaster
```

### Project Structure
```
Github_Sportscaster/
├── github_sportscaster_project/  # Django project settings
├── sportscaster/                  # Main application
│   ├── management/               # Management commands
│   │   └── commands/
│   │       └── monitor_github.py # GitHub monitoring service
│   ├── templates/                # HTML templates
│   ├── models.py                 # Database models
│   ├── views.py                  # Views and API endpoints
│   ├── services.py               # GitHub API service
│   ├── ai_commentary.py          # AI commentary generator
│   ├── consumers.py              # WebSocket consumers
│   ├── routing.py                # WebSocket routing
│   ├── admin.py                  # Admin configuration
│   ├── tests.py                  # Unit tests
│   └── urls.py                   # URL routing
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management script
└── README.md                     # This file
```

## Configuration

### GitHub API Rate Limiting
- Unauthenticated requests: 60 requests/hour
- Authenticated requests: 5,000 requests/hour
- Use a GitHub token for better rate limits

### Caching
Adjust caching settings in `.env`:
- `CACHE_TIMEOUT`: Cache duration in seconds
- `POLL_INTERVAL`: Event polling interval

### Production Deployment

For production deployment:

1. **Use Redis for Channels**
Update `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6379)],
        },
    },
}
```

2. **Use a production-ready database** (PostgreSQL recommended)

3. **Configure environment variables properly**
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS`

4. **Use a production ASGI server**
```bash
daphne -b 0.0.0.0 -p 8000 github_sportscaster_project.asgi:application
```

5. **Set up process manager** (systemd, supervisor, or Docker)

## Security Considerations

- Never commit `.env` file or expose API keys
- Use environment variables for sensitive configuration
- Enable HTTPS in production
- Configure CORS properly for WebSocket connections
- Regularly update dependencies for security patches

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of OWASP-BLT initiative.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Django and Django Channels teams
- GitHub API
- OpenAI for AI commentary capabilities
- OWASP-BLT community

---

Made with ❤️ by the OWASP-BLT Team