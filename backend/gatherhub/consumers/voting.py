"""
Voting-specific WebSocket consumer for real-time voting updates.
"""

import json
import logging
from channels.db import database_sync_to_async
from .base import BaseConsumer

logger = logging.getLogger(__name__)


class VotingConsumer(BaseConsumer):
    """WebSocket consumer for voting updates."""
    
    async def get_room_group_name(self):
        """Get the voting room group name."""
        return f"event_{self.event_slug}_voting"
    
    @database_sync_to_async
    def check_event_access(self):
        """Check if user can access the event for voting."""
        from apps.events.models import Event
        try:
            event = Event.objects.get(slug=self.event_slug)
            # Only allow voting on draft events
            return event.status == 'draft'
        except Event.DoesNotExist:
            return False
    
    async def connect(self):
        """Handle WebSocket connection for voting."""
        await super().connect()
        
        if self.user:
            # Send current voting data on connection
            voting_data = await self.get_voting_data()
            if voting_data:
                await self.send_json({
                    'type': 'voting_data',
                    'data': voting_data
                })
    
    @database_sync_to_async
    def get_voting_data(self):
        """Get current voting data for the event."""
        from apps.events.models import Event, TimeSlot
        from apps.voting.models import Vote
        
        try:
            event = Event.objects.get(slug=self.event_slug)
            timeslots = list(event.time_slots.all().values('id', 'datetime')) # type: ignore
            
            # Get vote counts for each timeslot
            for timeslot in timeslots:
                vote_count = Vote.objects.filter(timeslot_id=timeslot['id']).count()
                user_voted = Vote.objects.filter(
                    timeslot_id=timeslot['id'],
                    user=self.user
                ).exists()
                timeslot['vote_count'] = vote_count
                timeslot['user_voted'] = user_voted
            
            return {
                'event_slug': self.event_slug,
                'event_status': event.status,
                'timeslots': timeslots
            }
        except Event.DoesNotExist:
            return None
    
    # Message handlers
    async def handle_vote_add(self, data):
        """Handle vote addition request."""
        timeslot_id = data.get('timeslot_id')
        if not timeslot_id:
            await self.send_error('Missing timeslot_id')
            return
        
        result = await self.add_vote(timeslot_id)
        if result:
            await self.send_json({
                'type': 'vote_added',
                'data': result
            })
        else:
            await self.send_error('Failed to add vote')
    
    async def handle_vote_remove(self, data):
        """Handle vote removal request."""
        timeslot_id = data.get('timeslot_id')
        if not timeslot_id:
            await self.send_error('Missing timeslot_id')
            return
        
        result = await self.remove_vote(timeslot_id)
        if result:
            await self.send_json({
                'type': 'vote_removed',
                'data': result
            })
        else:
            await self.send_error('Failed to remove vote')
    
    @database_sync_to_async
    def add_vote(self, timeslot_id):
        """Add a vote for the user."""
        from apps.events.models import TimeSlot
        from apps.voting.models import Vote
        
        try:
            timeslot = TimeSlot.objects.get(
                id=timeslot_id,
                event__slug=self.event_slug
            )
            
            # Check if event is still in draft status
            if timeslot.event.status != 'draft':
                return None
            
            # Create or get vote
            vote, created = Vote.objects.get_or_create(
                user=self.user,
                timeslot=timeslot
            )
            
            if created:
                # Get updated vote count
                vote_count = Vote.objects.filter(timeslot=timeslot).count()
                return {
                    'timeslot_id': timeslot_id,
                    'user': {
                        'id': self.user.id, # type: ignore
                        'first_name': self.user.first_name, # type: ignore
                        'last_name': self.user.last_name, # type: ignore
                        'email': self.user.email # type: ignore
                    },
                    'new_vote_count': vote_count,
                    'timestamp': self.get_timestamp()
                }
            return None
            
        except TimeSlot.DoesNotExist:
            return None
    
    @database_sync_to_async
    def remove_vote(self, timeslot_id):
        """Remove a vote for the user."""
        from apps.events.models import TimeSlot
        from apps.voting.models import Vote
        
        try:
            timeslot = TimeSlot.objects.get(
                id=timeslot_id,
                event__slug=self.event_slug
            )
            
            # Check if event is still in draft status
            if timeslot.event.status != 'draft':
                return None
            
            # Remove vote
            deleted_count, _ = Vote.objects.filter(
                user=self.user,
                timeslot=timeslot
            ).delete()
            
            if deleted_count > 0:
                # Get updated vote count
                vote_count = Vote.objects.filter(timeslot=timeslot).count()
                return {
                    'timeslot_id': timeslot_id,
                    'user': {
                        'id': self.user.id, # type: ignore
                        'first_name': self.user.first_name, # type: ignore
                        'last_name': self.user.last_name, # type: ignore
                        'email': self.user.email # type: ignore
                    },
                    'new_vote_count': vote_count,
                    'timestamp': self.get_timestamp()
                }
            return None
            
        except TimeSlot.DoesNotExist:
            return None
    
    # Broadcast handlers for group messages
    async def vote_update(self, event):
        """Handle vote update broadcasts."""
        await self.send_json(event['message'])
    
    async def event_locked(self, event):
        """Handle event lock broadcasts - disable voting."""
        await self.send_json(event['message'])
