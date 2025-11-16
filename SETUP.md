# GitHub Sportscaster - Setup Guide

## Quick Start

Follow these steps to get the GitHub Sportscaster up and running on your local machine.

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- (Optional) Redis for production WebSocket support

### Step 1: Clone the Repository

```bash
git clone https://github.com/OWASP-BLT/Github_Sportscaster.git
cd Github_Sportscaster
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required for GitHub monitoring
GITHUB_TOKEN=your_github_personal_access_token

# Optional: For AI-powered commentary (falls back to template-based)
OPENAI_API_KEY=your_openai_api_key

# Django settings
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Getting a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "Sportscaster"
4. Select scopes: `public_repo`, `read:org`, `read:user`
5. Click "Generate token"
6. Copy the token and paste it in your `.env` file

### Step 5: Initialize Database

```bash
python manage.py migrate
```

### Step 6: Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 7: Set Up Demo Data (Optional)

To quickly test the application with demo channels:

```bash
python manage.py setup_demo
```

This creates two channels:
- **Hot Python Projects**: Monitoring popular Python repositories
- **JavaScript Frameworks**: Monitoring popular JavaScript frameworks

### Step 8: Start the Application

You need to run two commands in separate terminals:

**Terminal 1 - Web Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Event Monitor:**
```bash
python manage.py monitor_github
```

### Step 9: Access the Application

Open your browser and navigate to:
- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## Creating Your Own Channels

### Via Admin Panel

1. Log in to the admin panel at http://localhost:8000/admin
2. Click on "Channels" → "Add Channel"
3. Fill in the details:
   - **Name**: Give your channel a descriptive name
   - **Description**: Describe what it monitors
   - **Scope**: Choose from:
     - `all` - Monitor all of GitHub
     - `org` - Monitor a specific organization
     - `repo` - Monitor specific repositories
     - `tag` - Monitor repositories with specific tags
     - `custom` - Custom list of repositories
   - **Is active**: Check to enable monitoring

4. Click "Save"
5. Add monitored entities:
   - Go to "Monitored Entities" → "Add Monitored Entity"
   - Select your channel
   - Enter repository name in format: `owner/repository`
   - Example: `facebook/react`, `django/django`
   - Set as active
   - Click "Save"

### Monitoring Commands

The `monitor_github` command supports several options:

```bash
# Default: Poll every 60 seconds
python manage.py monitor_github

# Custom polling interval (in seconds)
python manage.py monitor_github --interval 120

# Monitor specific channel only
python manage.py monitor_github --channel-id 1
```

## API Endpoints

Test the API endpoints:

```bash
# List all channels
curl http://localhost:8000/api/channels/

# Get events for channel 1
curl http://localhost:8000/api/channel/1/events/

# Get leaderboard for channel 1
curl http://localhost:8000/api/channel/1/leaderboard/

# Test AI commentary generation
curl -X POST http://localhost:8000/api/test-commentary/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "star", "repository": "owner/repo", "actor": "username"}'
```

## WebSocket Connection

The application uses WebSocket for real-time updates. Connect to:

```
ws://localhost:8000/ws/sportscaster/<channel_id>/
```

### JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sportscaster/1/');

ws.onopen = function(e) {
    console.log('Connected to sportscaster');
};

ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Received:', data);
};
```

## Running Tests

Run the test suite:

```bash
# Run all tests
python manage.py test sportscaster

# Run with verbose output
python manage.py test sportscaster --verbosity 2

# Run specific test class
python manage.py test sportscaster.tests.ChannelModelTest
```

## Production Deployment

For production deployment, see the [README.md](README.md) file for detailed instructions on:

- Using Redis for channel layers
- Configuring PostgreSQL database
- Setting up HTTPS
- Using Daphne or Uvicorn as ASGI server
- Process management with systemd or Docker

## Troubleshooting

### Issue: WebSocket not connecting

**Solution**: Make sure the Django server is running with ASGI support (automatically handled when using `manage.py runserver` with channels installed).

### Issue: No events showing up

**Possible causes**:
1. Monitor command not running - Start it with `python manage.py monitor_github`
2. No GitHub token - Add `GITHUB_TOKEN` to your `.env` file
3. No monitored entities - Add repositories via admin panel
4. Rate limiting - GitHub API has rate limits (60/hour without token, 5000/hour with token)

### Issue: AI commentary not working

**Solution**: The application falls back to template-based commentary if OpenAI API key is not configured. This is by design and works perfectly fine without AI integration.

### Issue: Database errors

**Solution**: Run migrations:
```bash
python manage.py migrate
```

## Getting Help

If you encounter issues:

1. Check the logs in the terminal where you're running the server
2. Check the browser console for JavaScript errors
3. Verify your `.env` configuration
4. Make sure all dependencies are installed
5. Open an issue on GitHub with details about the error

## Next Steps

- Explore the codebase in the `sportscaster/` directory
- Customize the templates in `sportscaster/templates/`
- Add more event types in `sportscaster/services.py`
- Integrate with other event sources
- Customize AI commentary in `sportscaster/ai_commentary.py`

Happy monitoring! 🎙️
