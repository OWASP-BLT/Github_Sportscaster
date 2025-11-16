# GitHub Sportscaster 🎙️

An AI-powered GitHub activity announcer that provides live sportscaster-style commentary on GitHub events. Watch repositories, organizations, and topics come alive with real-time play-by-play commentary, leaderboards, and visual displays!

## Features

🎯 **Live GitHub Monitoring** - Track stars, forks, pull requests, commits, issues, and releases in real-time

🎙️ **AI-Powered Commentary** - Get enthusiastic sportscaster-style commentary on GitHub activity (with optional OpenAI integration for enhanced AI commentary)

📊 **Real-time Leaderboards** - See rankings for repositories and users across multiple metrics

🎨 **Visual Display** - Animated frames with project logos, user avatars, and live statistics

⚙️ **Highly Configurable** - Monitor by organization, repository, topic/tag, or curated lists

🔌 **Extensible** - Modular architecture for adding custom commentary styles and event types

🌐 **Web Interface** - Built-in web server with live streaming capabilities

## Architecture

```
sportscaster/
├── api/            # GitHub API integration
├── commentary/     # AI commentary generation
├── config/         # Configuration management
├── core/           # Event monitoring and leaderboard
├── visualization/  # Frame rendering
├── app.py          # Main application
└── server.py       # Web server
```

## Installation

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token ([create one here](https://github.com/settings/tokens))
- (Optional) OpenAI API Key for enhanced AI commentary

### Setup

1. Clone the repository:
```bash
git clone https://github.com/OWASP-BLT/Github_Sportscaster.git
cd Github_Sportscaster
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Create a configuration file (or use examples):
```bash
cp examples/simple_config.yaml config.yaml
# Edit config.yaml to customize your channels
```

## Configuration

The sportscaster is configured using YAML files. Here's a basic example:

```yaml
github_token: ${GITHUB_TOKEN}

channels:
  - name: "My Channel"
    description: "Monitoring my favorite repos"
    repositories:
      - "octocat/Hello-World"
      - "github/gitignore"
    event_types:
      - star
      - fork
      - pull_request
    commentary_style: "enthusiastic"
```

### Channel Configuration Options

- **name**: Channel identifier
- **description**: Channel description
- **organizations**: List of GitHub organizations to monitor
- **repositories**: List of repositories (format: "owner/repo")
- **tags**: List of topics/tags to search and monitor
- **curated_lists**: Custom curated repository lists
- **event_types**: Events to monitor (star, fork, pull_request, commit, issue, release)
- **leaderboard_metrics**: Metrics to track (stars, forks, pull_requests, commits)
- **commentary_style**: Style of commentary (enthusiastic, professional, dramatic, casual)
- **show_avatars**: Display user avatars (true/false)
- **show_logos**: Display project logos (true/false)

See `examples/config.yaml` for more detailed configuration examples.

## Usage

### Run as Console Application

Monitor GitHub activity with console output:

```bash
python -m sportscaster.app
```

### Run as Web Server

Start the web interface with live streaming:

```bash
python -m sportscaster.server
```

Then open your browser to `http://localhost:5000` to see the live sportscaster!

### API Endpoints

The web server provides several REST API endpoints:

- `GET /` - Web interface
- `GET /api/state` - Current sportscaster state (JSON)
- `GET /api/events` - Recent events (JSON)
- `GET /api/leaderboard` - Leaderboard data (JSON)
- `GET /frame` - Current frame as PNG image
- `GET /api/stream` - Server-sent events stream

### Example API Usage

```bash
# Get current state
curl http://localhost:5000/api/state

# Get recent events
curl http://localhost:5000/api/events

# Download current frame
curl http://localhost:5000/frame -o frame.png
```

## Commentary Styles

The sportscaster supports multiple commentary styles:

### Enthusiastic (Default)
```
🌟 INCREDIBLE! octocat just starred Hello-World! The crowd goes wild!
```

### Professional
```
⭐ Hello-World receives a star from octocat.
```

### Dramatic
```
✨ In a stunning turn of events, octocat bestows a star upon Hello-World!
```

### AI-Enhanced (with OpenAI)
Enable by setting `OPENAI_API_KEY` in your environment. The AI will generate unique, contextual commentary for each event.

## Use Cases

### 1. Organization Activity Dashboard
Monitor all repositories in your organization to see what's happening in real-time.

### 2. Open Source Project Tracking
Track activity on multiple open source projects you're interested in.

### 3. Hackathon Leaderboard
Create a live leaderboard during hackathons to track participant activity.

### 4. Community Engagement
Display live GitHub activity at conferences or meetups.

### 5. Repository Analytics
Get insights into repository popularity and contributor activity.

## Extensibility

The modular architecture makes it easy to extend:

### Add Custom Commentary Styles

Edit `sportscaster/commentary/generator.py` to add new template sets.

### Add Custom Event Filters

Extend `sportscaster/core/monitor.py` to filter or transform events.

### Custom Visualizations

Modify `sportscaster/visualization/renderer.py` to change the display layout.

### Integration with Other Platforms

The API can be integrated with streaming platforms, Discord bots, Slack apps, etc.

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

- `sportscaster/api/` - GitHub API client and event models
- `sportscaster/commentary/` - Commentary generation (template and AI-based)
- `sportscaster/config/` - Configuration management with Pydantic
- `sportscaster/core/` - Event monitoring and leaderboard tracking
- `sportscaster/visualization/` - Frame rendering with PIL
- `sportscaster/app.py` - Main application orchestrator
- `sportscaster/server.py` - Flask web server
- `examples/` - Example configuration files
- `tests/` - Test suite

## Troubleshooting

### Rate Limiting

GitHub API has rate limits. With authentication, you get 5,000 requests/hour. The sportscaster respects these limits by:
- Polling at configurable intervals (default: 60 seconds)
- Batching repository queries
- Caching recent events

### No Events Showing

- Ensure your GitHub token has proper permissions
- Check that repositories are public or your token has access
- Verify the configuration file is properly formatted
- Check logs for API errors

### Performance

For monitoring many repositories:
- Increase `poll_interval` to reduce API calls
- Limit `max_events_per_cycle`
- Monitor fewer event types

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- New features
- Documentation improvements
- Additional commentary styles
- Performance optimizations

## License

MIT License - see LICENSE file for details

## Credits

Built for the OWASP Bug Logging Tool project as an innovative way to visualize and celebrate open source contribution activity.

## Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

Made with ❤️ for the open source community