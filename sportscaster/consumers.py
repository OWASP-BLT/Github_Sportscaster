"""
WebSocket consumers for real-time event streaming
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)


class SportscasterConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live sportscaster events"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.channel_id = self.scope['url_route']['kwargs'].get('channel_id', 'default')
        self.room_group_name = f'sportscaster_{self.channel_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected to channel {self.channel_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from channel {self.channel_id}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            # Handle different message types
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
    
    async def event_message(self, event):
        """Handle event messages from channel layer"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))
    
    async def leaderboard_update(self, event):
        """Handle leaderboard update messages"""
        await self.send(text_data=json.dumps(event['data']))
    
    async def commentary_message(self, event):
        """Handle commentary messages"""
        await self.send(text_data=json.dumps(event['data']))
