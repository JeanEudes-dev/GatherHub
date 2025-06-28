"""
Django signals for real-time event updates.
"""

import json
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Event, TimeSlot

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@receiver(post_save, sender=Event)
def event_updated_signal(sender, instance, created, **kwargs):
    """Signal handler for when an event is created or updated."""
    if not created and channel_layer:  # Only handle updates, not creation
        # Get event slug
        event_slug = instance.slug
        
        # Determine what changed (basic implementation)
        action = 'modified'
        changes = {}
        
        # Check for status change (event locking)
        if hasattr(instance, '_state') and instance._state.adding is False:
            # This is an update - check if status changed to locked
            if instance.status == 'locked':
                action = 'locked'
                changes['status'] = {'to': 'locked'}
        
        # Prepare message data
        message_data = {
            'type': 'event_update',
            'action': action,
            'data': {
                'event': {
                    'slug': instance.slug,
                    'title': instance.title,
                    'status': instance.status
                },
                'changes': changes,
                'timestamp': instance.updated_at.isoformat()
            }
        }
        
        # Broadcast to all related rooms
        rooms = [
            f"event_{event_slug}",
            f"event_{event_slug}_voting",
            f"event_{event_slug}_tasks"
        ]
        
        for room in rooms:
            async_to_sync(channel_layer.group_send)(
                room,
                {
                    'type': 'event_update' if 'voting' not in room else 'event_locked',
                    'message': message_data
                }
            )
        
        logger.info(f"Event {action} broadcast sent for event {event_slug}")


@receiver(post_save, sender=TimeSlot)
def timeslot_added_signal(sender, instance, created, **kwargs):
    """Signal handler for when a timeslot is added."""
    if created and channel_layer:
        # Get event slug
        event_slug = instance.event.slug
        
        # Prepare message data
        message_data = {
            'type': 'event_update',
            'action': 'timeslot_added',
            'data': {
                'event': {
                    'slug': instance.event.slug,
                    'title': instance.event.title
                },
                'timeslot': {
                    'id': instance.id,
                    'datetime': instance.datetime.isoformat()
                },
                'timestamp': instance.created_at.isoformat()
            }
        }
        
        # Broadcast to all related rooms
        rooms = [
            f"event_{event_slug}",
            f"event_{event_slug}_voting",
            f"event_{event_slug}_tasks"
        ]
        
        for room in rooms:
            async_to_sync(channel_layer.group_send)(
                room,
                {
                    'type': 'timeslot_added',
                    'message': message_data
                }
            )
        
        logger.info(f"Timeslot added broadcast sent for event {event_slug}")


@receiver(post_delete, sender=TimeSlot)
def timeslot_removed_signal(sender, instance, **kwargs):
    """Signal handler for when a timeslot is removed."""
    if channel_layer:
        # Get event slug
        event_slug = instance.event.slug
        
        # Prepare message data
        message_data = {
            'type': 'event_update',
            'action': 'timeslot_removed',
            'data': {
                'event': {
                    'slug': instance.event.slug,
                    'title': instance.event.title
                },
                'timeslot': {
                    'id': instance.id,
                    'datetime': instance.datetime.isoformat()
                },
                'timestamp': instance.created_at.isoformat()
            }
        }
        
        # Broadcast to all related rooms
        rooms = [
            f"event_{event_slug}",
            f"event_{event_slug}_voting",
            f"event_{event_slug}_tasks"
        ]
        
        for room in rooms:
            async_to_sync(channel_layer.group_send)(
                room,
                {
                    'type': 'timeslot_removed',
                    'message': message_data
                }
            )
        
        logger.info(f"Timeslot removed broadcast sent for event {event_slug}")
