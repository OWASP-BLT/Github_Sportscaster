# ⚡ GitHub Activity Sportscaster

A real-time leaderboard of GitHub repository activity that you can keep open and watch as repositories compete for the top spots!

## 🎯 Features

- **Live Activity Tracking**: Monitors the latest GitHub public events globally
- **Dynamic Leaderboard**: Repositories are ranked by their activity count
- **Visual Effects**:
  - 💫 **Blink Animation**: Cards flash when new activity is detected
  - 🎉 **Celebration Effect**: Confetti animation when a repo moves up in the rankings
  - ✨ **Smooth Transitions**: Beautiful animations throughout
- **Grid Layout**: Responsive grid that works on all screen sizes
- **Real-time Stats**: Track total repositories and events processed
- **Auto-refresh**: Updates every 30 seconds with the latest activity

## 🚀 Live Demo

Visit the live page at: https://owasp-blt.github.io/Github_Sportscaster/

## 📖 How It Works

The page fetches data from the GitHub Events API (`https://api.github.com/events`) which provides the latest public events happening across GitHub. Each event is associated with a repository, and the page:

1. Counts the number of events per repository
2. Sorts repositories by their activity count
3. Displays them in a beautiful grid layout
4. Animates cards when new activity comes in
5. Shows celebration effects when repositories climb the leaderboard

## 🎨 Visual Design

- Beautiful gradient background (purple theme)
- Glassmorphic cards with backdrop blur
- Responsive grid layout (adapts to screen size)
- Smooth hover effects
- Real-time animations for activity and rank changes

## 🛠️ Technical Details

- **Single File Application**: Everything in one HTML file (HTML + CSS + JavaScript)
- **No Dependencies**: Pure vanilla JavaScript, no frameworks needed
- **GitHub Pages Compatible**: Ready to deploy as a static site
- **Demo Mode**: Automatically falls back to simulated data if API is blocked

## 📝 Usage

Simply open the page and watch! The leaderboard will:
- Update every 30 seconds
- Show new repositories as they appear in GitHub's public timeline
- Highlight repositories with new activity
- Celebrate when repositories move up in the rankings

## 🔧 Development

To run locally:
```bash
# Clone the repository
git clone https://github.com/OWASP-BLT/Github_Sportscaster.git
cd Github_Sportscaster

# Serve the file (any HTTP server works)
python3 -m http.server 8080

# Open http://localhost:8080 in your browser
```

## 📄 License

This project is open source and available under the MIT License.