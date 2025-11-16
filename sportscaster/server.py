"""Web server for GitHub Sportscaster streaming"""

import asyncio
import logging
from flask import Flask, jsonify, send_file, Response
from flask_cors import CORS
import io
import json
from threading import Thread

from sportscaster.config import Settings
from sportscaster.app import Sportscaster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global sportscaster instance
sportscaster: Sportscaster = None


def create_app(settings: Settings) -> Flask:
    """
    Create Flask application
    
    Args:
        settings: Application settings
        
    Returns:
        Flask app
    """
    app = Flask(__name__)
    CORS(app)
    
    global sportscaster
    sportscaster = Sportscaster(settings)
    
    @app.route('/')
    def index():
        """Main page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GitHub Sportscaster</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    background: #1a1a2e;
                    color: #eee;
                    font-family: Arial, sans-serif;
                }
                h1 {
                    color: #ffd700;
                    text-align: center;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .frame-container {
                    text-align: center;
                    margin: 20px 0;
                }
                .frame {
                    max-width: 100%;
                    border: 3px solid #ffd700;
                    border-radius: 10px;
                }
                .info {
                    background: #16213e;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }
                .api-links {
                    background: #16213e;
                    padding: 20px;
                    border-radius: 10px;
                }
                .api-links a {
                    color: #ffd700;
                    text-decoration: none;
                    display: block;
                    margin: 10px 0;
                }
                .api-links a:hover {
                    text-decoration: underline;
                }
            </style>
            <script>
                // Auto-refresh frame
                setInterval(() => {
                    const img = document.getElementById('live-frame');
                    img.src = '/frame?' + new Date().getTime();
                }, 5000);
                
                // Update state
                setInterval(() => {
                    fetch('/api/state')
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('commentary').textContent = data.commentary;
                        });
                }, 2000);
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🎙️ GitHub Sportscaster - Live Stream</h1>
                
                <div class="info">
                    <h2>Current Commentary:</h2>
                    <p id="commentary" style="font-size: 18px; font-weight: bold;">Loading...</p>
                </div>
                
                <div class="frame-container">
                    <img id="live-frame" class="frame" src="/frame" alt="Live Frame">
                </div>
                
                <div class="api-links">
                    <h2>API Endpoints:</h2>
                    <a href="/api/state">GET /api/state - Current state</a>
                    <a href="/api/events">GET /api/events - Recent events</a>
                    <a href="/api/leaderboard">GET /api/leaderboard - Leaderboard data</a>
                    <a href="/frame">GET /frame - Current frame image</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/api/state')
    def get_state():
        """Get current sportscaster state"""
        try:
            state = sportscaster.get_current_state()
            return jsonify(state)
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/events')
    def get_events():
        """Get recent events"""
        try:
            return jsonify({
                "events": sportscaster.recent_events[-20:]
            })
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/leaderboard')
    def get_leaderboard():
        """Get leaderboard data"""
        try:
            return jsonify(sportscaster.current_leaderboard)
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/frame')
    def get_frame():
        """Get current frame as image"""
        try:
            img = sportscaster.render_current_frame()
            
            # Convert to bytes
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            return send_file(img_io, mimetype='image/png')
        except Exception as e:
            logger.error(f"Error rendering frame: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/stream')
    def stream():
        """Server-sent events stream"""
        def event_stream():
            while True:
                try:
                    state = sportscaster.get_current_state()
                    yield f"data: {json.dumps(state)}\n\n"
                    asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error in stream: {e}")
                    break
        
        return Response(event_stream(), mimetype='text/event-stream')
    
    return app


def run_sportscaster_thread(sportscaster_instance: Sportscaster):
    """Run sportscaster in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sportscaster_instance.start())


def main():
    """Main entry point for server"""
    # Load settings
    try:
        settings = Settings.load_from_file("config.yaml")
        logger.info("Loaded configuration from config.yaml")
    except FileNotFoundError:
        logger.info("No config.yaml found, using default settings")
        settings = Settings()
        
        # Add a default channel
        from sportscaster.config import ChannelConfig
        if not settings.channels:
            default_channel = ChannelConfig(
                name="default",
                description="Default monitoring channel",
                organizations=[],
                repositories=["octocat/Hello-World"],
                tags=["python"],
            )
            settings.channels.append(default_channel)
    
    # Create Flask app
    app = create_app(settings)
    
    # Start sportscaster in background thread
    sportscaster_thread = Thread(target=run_sportscaster_thread, args=(sportscaster,), daemon=True)
    sportscaster_thread.start()
    
    # Run Flask server
    logger.info(f"Starting web server on {settings.flask_host}:{settings.flask_port}")
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=False,
        threaded=True
    )


if __name__ == "__main__":
    main()
