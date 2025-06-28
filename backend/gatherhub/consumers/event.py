"""
Event-specific WebSocket consumer for real-time event updates.
"""

import json
import logging
from channels.db import database_sync_to_async
from .base import BaseConsumer

logger = logging.getLogger(__name__)


class EventConsumer(BaseConsumer):
    """WebSocket consumer for event-specific updates."""
    
    async def get_room_group_name(self):
        """Get the event room group name."""
        return f"event_{self.event_slug}"
    
    @database_sync_to_async
    def check_event_access(self):
        """Check if user can access the event."""
        from apps.events.models import Event
        try:
            event = Event.objects.get(slug=self.event_slug)
            # Basic access control - all authenticated users can access events
            # This can be enhanced with proper membership checking
            return True
        except Event.DoesNotExist:
            return False
    
    async def connect(self):
        """Handle WebSocket connection for events."""
        await super().connect()
        
        if self.user:
            # Send current event data on connection
            event_data = await self.get_event_data()
            if event_data:
                await self.send_json({
                    'type': 'event_data',
                    'data': event_data
                })
    
    @database_sync_to_async
    def get_event_data(self):
        """Get current event data."""
        from apps.events.models import Event
        from apps.events.serializers import EventDetailSerializer
        
        try:
            event = Event.objects.prefetch_related('time_slots__votes').get(slug=self.event_slug)
            serializer = EventDetailSerializer(event)
            return serializer.data
        except Event.DoesNotExist:
            return None
    
    # Message handlers
    async def handle_ping(self, data):
        """Handle ping messages."""
        await self.send_json({
            'type': 'pong',
            'data': {
                'timestamp': self.get_timestamp()
            }
        })
    
    # Broadcast handlers for group messages
    async def event_update(self, event):
        """Handle event update broadcasts."""
        await self.send_json(event['message'])
    
    async def event_locked(self, event):
        """Handle event lock broadcasts."""
        await self.send_json(event['message'])
    
    async def timeslot_added(self, event):
        """Handle timeslot addition broadcasts."""
        await self.send_json(event['message'])
    
    async def timeslot_removed(self, event):
        """Handle timeslot removal broadcasts."""
        await self.send_json(event['message'])
