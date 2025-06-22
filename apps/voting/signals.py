"""
Django signals for real-time voting updates.
"""

import json
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Vote

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@receiver(post_save, sender=Vote)
def vote_added_signal(sender, instance, created, **kwargs):
    """Signal handler for when a vote is added."""
    if created and channel_layer:
        # Get event slug
        event_slug = instance.timeslot.event.slug
        
        # Prepare message data
        message_data = {
            'type': 'vote_update',
            'action': 'added',
            'data': {
                'timeslot_id': instance.timeslot.id,
                'user': {
                    'id': instance.user.id,
                    'name': instance.user.name,
                    'email': instance.user.email
                },
                'new_vote_count': instance.timeslot.votes.count(),
                'timestamp': instance.created_at.isoformat()
            }
        }
        
        # Broadcast to voting room
        async_to_sync(channel_layer.group_send)(
            f"event_{event_slug}_voting",
            {
                'type': 'vote_update',
                'message': message_data
            }
        )
        
        # Also broadcast to general event room
        async_to_sync(channel_layer.group_send)(
            f"event_{event_slug}",
            {
                'type': 'event_update',
                'message': message_data
            }
        )
        
        logger.info(f"Vote added broadcast sent for event {event_slug}")


@receiver(post_delete, sender=Vote)
def vote_removed_signal(sender, instance, **kwargs):
    """Signal handler for when a vote is removed."""
    if channel_layer:
        # Get event slug
        event_slug = instance.timeslot.event.slug
        
        # Get updated vote count (after deletion)
        new_vote_count = instance.timeslot.votes.count()
        
        # Prepare message data
        message_data = {
            'type': 'vote_update',
            'action': 'removed',
            'data': {
                'timeslot_id': instance.timeslot.id,
                'user': {
                    'id': instance.user.id,
                    'name': instance.user.name,
                    'email': instance.user.email
                },
                'new_vote_count': new_vote_count,
                'timestamp': instance.created_at.isoformat()
            }
        }
        
        # Broadcast to voting room
        async_to_sync(channel_layer.group_send)(
            f"event_{event_slug}_voting",
            {
                'type': 'vote_update',
                'message': message_data
            }
        )
        
        # Also broadcast to general event room
        async_to_sync(channel_layer.group_send)(
            f"event_{event_slug}",
            {
                'type': 'event_update',
                'message': message_data
            }
        )
        
        logger.info(f"Vote removed broadcast sent for event {event_slug}")
