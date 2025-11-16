"""Visual rendering for sportscaster display"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import requests

logger = logging.getLogger(__name__)


class SportscastRenderer:
    """Renders visual elements for the sportscaster"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        """
        Initialize renderer
        
        Args:
            width: Output width in pixels
            height: Output height in pixels
        """
        self.width = width
        self.height = height
        self.background_color = (20, 20, 40)  # Dark blue background
        self.text_color = (255, 255, 255)  # White text
        self.accent_color = (255, 215, 0)  # Gold accent
        
        # Try to load fonts
        try:
            self.title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            self.header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            self.body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except Exception as e:
            logger.warning(f"Could not load custom fonts: {e}")
            self.title_font = ImageFont.load_default()
            self.header_font = ImageFont.load_default()
            self.body_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
    
    def render_frame(
        self,
        commentary: str,
        leaderboard: Dict[str, Any],
        recent_events: List[Dict[str, Any]],
        show_avatars: bool = True
    ) -> Image.Image:
        """
        Render a complete frame
        
        Args:
            commentary: Current commentary text
            leaderboard: Leaderboard data
            recent_events: List of recent events
            show_avatars: Whether to show user avatars
            
        Returns:
            PIL Image
        """
        # Create base image
        img = Image.new('RGB', (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw title banner
        self._draw_title_banner(draw, "GitHub Sportscaster")
        
        # Draw commentary section (center)
        self._draw_commentary(draw, commentary)
        
        # Draw leaderboard (right side)
        self._draw_leaderboard(draw, leaderboard)
        
        # Draw recent events ticker (bottom)
        self._draw_event_ticker(draw, recent_events)
        
        # Draw timestamp
        self._draw_timestamp(draw)
        
        return img
    
    def _draw_title_banner(self, draw: ImageDraw, title: str):
        """Draw the title banner at the top"""
        banner_height = 100
        
        # Draw banner background
        draw.rectangle(
            [(0, 0), (self.width, banner_height)],
            fill=(40, 40, 80),
            outline=self.accent_color,
            width=3
        )
        
        # Draw title text
        bbox = draw.textbbox((0, 0), title, font=self.title_font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        
        draw.text(
            (text_x, 25),
            title,
            fill=self.accent_color,
            font=self.title_font
        )
    
    def _draw_commentary(self, draw: ImageDraw, commentary: str):
        """Draw the commentary section"""
        section_top = 120
        section_height = 300
        section_left = 50
        section_width = self.width - 600
        
        # Draw section background
        draw.rectangle(
            [(section_left, section_top), (section_left + section_width, section_top + section_height)],
            fill=(30, 30, 60),
            outline=self.accent_color,
            width=2
        )
        
        # Draw section title
        draw.text(
            (section_left + 20, section_top + 10),
            "🎙️ LIVE COMMENTARY",
            fill=self.accent_color,
            font=self.header_font
        )
        
        # Draw commentary text (word wrap)
        self._draw_wrapped_text(
            draw,
            commentary,
            section_left + 20,
            section_top + 70,
            section_width - 40,
            self.body_font,
            self.text_color
        )
    
    def _draw_leaderboard(self, draw: ImageDraw, leaderboard: Dict[str, Any]):
        """Draw the leaderboard section"""
        section_top = 120
        section_height = 700
        section_left = self.width - 500
        section_width = 450
        
        # Draw section background
        draw.rectangle(
            [(section_left, section_top), (section_left + section_width, section_top + section_height)],
            fill=(30, 30, 60),
            outline=self.accent_color,
            width=2
        )
        
        # Draw section title
        draw.text(
            (section_left + 20, section_top + 10),
            "🏆 LEADERBOARD",
            fill=self.accent_color,
            font=self.header_font
        )
        
        # Draw leaderboard entries
        y_offset = section_top + 70
        
        if not leaderboard:
            draw.text(
                (section_left + 20, y_offset),
                "Collecting data...",
                fill=self.text_color,
                font=self.body_font
            )
            return
        
        # Draw top repositories
        for key, entries in leaderboard.items():
            if not entries or not key.startswith("top_repos"):
                continue
            
            metric = key.replace("top_repos_", "")
            draw.text(
                (section_left + 20, y_offset),
                f"Top {metric.title()}:",
                fill=self.accent_color,
                font=self.body_font
            )
            y_offset += 35
            
            for i, entry in enumerate(entries[:5]):
                repo = entry.get("repository", "")
                score = entry.get("score", 0)
                
                text = f"{i+1}. {repo}: {score}"
                draw.text(
                    (section_left + 40, y_offset),
                    text,
                    fill=self.text_color,
                    font=self.small_font
                )
                y_offset += 28
            
            y_offset += 20
            
            if y_offset > section_top + section_height - 50:
                break
    
    def _draw_event_ticker(self, draw: ImageDraw, events: List[Dict[str, Any]]):
        """Draw the event ticker at the bottom"""
        ticker_height = 120
        ticker_top = self.height - ticker_height
        
        # Draw ticker background
        draw.rectangle(
            [(0, ticker_top), (self.width, self.height)],
            fill=(40, 40, 80),
            outline=self.accent_color,
            width=2
        )
        
        # Draw ticker title
        draw.text(
            (20, ticker_top + 10),
            "📊 RECENT ACTIVITY",
            fill=self.accent_color,
            font=self.body_font
        )
        
        # Draw recent events
        if not events:
            return
        
        x_offset = 20
        y_offset = ticker_top + 50
        
        for event in events[-5:]:  # Show last 5 events
            event_type = event.get("event_type", "")
            actor = event.get("actor", "")
            repo = event.get("repository", "")
            
            # Map event types to emojis
            emoji_map = {
                "star": "⭐",
                "fork": "🍴",
                "pull_request": "📝",
                "commit": "💻",
                "issue": "🐛",
                "release": "🚀",
            }
            
            emoji = emoji_map.get(event_type, "📢")
            text = f"{emoji} {actor}"
            
            draw.text(
                (x_offset, y_offset),
                text,
                fill=self.text_color,
                font=self.small_font
            )
            
            x_offset += 200
            
            if x_offset > self.width - 200:
                break
    
    def _draw_timestamp(self, draw: ImageDraw):
        """Draw current timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        bbox = draw.textbbox((0, 0), timestamp, font=self.small_font)
        text_width = bbox[2] - bbox[0]
        
        draw.text(
            (self.width - text_width - 20, 20),
            timestamp,
            fill=self.text_color,
            font=self.small_font
        )
    
    def _draw_wrapped_text(
        self,
        draw: ImageDraw,
        text: str,
        x: int,
        y: int,
        max_width: int,
        font: ImageFont.FreeTypeFont,
        color: tuple
    ):
        """Draw text with word wrapping"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        line_height = 35
        for i, line in enumerate(lines):
            draw.text(
                (x, y + i * line_height),
                line,
                fill=color,
                font=font
            )
    
    def save_frame(self, img: Image.Image, output_path: str):
        """
        Save frame to file
        
        Args:
            img: PIL Image
            output_path: Path to save image
        """
        img.save(output_path)
        logger.info(f"Saved frame to {output_path}")
