# Quick Start Guide

Get your GitHub Sportscaster up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- GitHub Personal Access Token ([create one here](https://github.com/settings/tokens))
  - Select scopes: `public_repo` (or `repo` for private repos)

## Installation

### 1. Clone and Install

```bash
git clone https://github.com/OWASP-BLT/Github_Sportscaster.git
cd Github_Sportscaster
pip install -r requirements.txt
```

### 2. Configure Your Token

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your GitHub token:

```
GITHUB_TOKEN=your_github_token_here
```

### 3. Try the Demo

Run a quick demo without full setup:

```bash
python demo.py
```

This will show you sample commentary, leaderboards, and generate a visualization frame.

## Running the Sportscaster

### Option 1: Simple Config (Recommended for First Time)

Create a simple `config.yaml`:

```yaml
github_token: ${GITHUB_TOKEN}

channels:
  - name: "My First Channel"
    repositories:
      - "octocat/Hello-World"
      - "github/gitignore"
    event_types:
      - star
      - fork
      - pull_request
    commentary_style: "enthusiastic"
```

### Option 2: Use Example Config

```bash
cp examples/simple_config.yaml config.yaml
```

### Start the Web Server

```bash
python -m sportscaster.server
```

Open your browser to: **http://localhost:5000**

You'll see:
- Live commentary as events happen
- Real-time leaderboards
- Visual sportscaster display
- Recent activity feed

## What to Monitor

### Monitor Specific Repositories

```yaml
repositories:
  - "facebook/react"
  - "microsoft/vscode"
  - "tensorflow/tensorflow"
```

### Monitor an Organization

```yaml
organizations:
  - "OWASP"
  - "google"
```

### Monitor by Topic/Tag

```yaml
tags:
  - "machine-learning"
  - "web-framework"
  - "security"
```

## Commentary Styles

Try different styles by setting `commentary_style`:

- **enthusiastic** - "🌟 INCREDIBLE! user just starred repo! The crowd goes wild!"
- **professional** - "⭐ repo receives a star from user."
- **dramatic** - "✨ In a stunning turn of events, user bestows a star upon repo!"

## API Endpoints

Once running, access these endpoints:

- `GET /` - Web interface
- `GET /api/state` - Current state (JSON)
- `GET /api/events` - Recent events (JSON)
- `GET /api/leaderboard` - Leaderboard data (JSON)
- `GET /frame` - Current frame image (PNG)

## Common Issues

### "No module named 'sportscaster'"

Make sure you're in the project directory and run:
```bash
pip install -r requirements.txt
```

### "GitHub token is required"

Ensure your `.env` file has `GITHUB_TOKEN=your_token_here`

### Rate Limiting

GitHub API allows 5,000 requests/hour with authentication. The default poll interval of 60 seconds is conservative. Adjust `poll_interval` in your config if needed.

### No Events Showing

- Check that repositories are public (or your token has access)
- Wait 1-2 minutes for the first poll cycle
- Check logs for errors
- Try monitoring more active repositories

## Next Steps

1. **Add OpenAI Commentary** (Optional)
   - Get an OpenAI API key
   - Add `OPENAI_API_KEY=your_key_here` to `.env`
   - AI will generate unique commentary for each event

2. **Monitor Your Organization**
   - Add your org to the config
   - Track all your team's activity

3. **Customize the Display**
   - Edit `sportscaster/visualization/renderer.py`
   - Change colors, fonts, layout

4. **Create Custom Commentary**
   - Add templates to `sportscaster/commentary/generator.py`
   - Create your own commentary style

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- See [examples/config.yaml](examples/config.yaml) for advanced configuration
- Open an issue on GitHub for support

## Have Fun! 🎙️

Your GitHub Sportscaster is now live! Watch as it announces every star, fork, commit, and release with sportscaster enthusiasm!
