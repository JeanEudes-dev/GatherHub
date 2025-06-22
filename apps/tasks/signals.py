"""
Django signals for real-time task updates.
"""

import json
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@receiver(post_save, sender=Task)
def task_updated_signal(sender, instance, created, **kwargs):
    """Signal handler for when a task is created or updated."""
    if channel_layer:
        # Get event slug
        event_slug = instance.event.slug
        
        # Determine action
        action = 'created' if created else 'updated'
        
        # Prepare task data
        task_data = {
            'id': instance.id,
            'title': instance.title,
            'status': instance.status,
            'assigned_to': {
                'id': instance.assigned_to.id,
                'name': instance.assigned_to.name
            } if instance.assigned_to else None
        }
        
        # Prepare message data
        message_data = {
            'type': 'task_update',
            'action': action,
            'data': {
                'task': task_data,
                'timestamp': instance.updated_at.isoformat()
            }
        }
        
        # For updates, try to get change information (this is basic, could be enhanced)
        if not created:
            # In a real implementation, you might want to track field changes
            # For now, we'll just indicate it was updated
            message_data['data']['changes'] = {'updated_at': True}
        
        # Broadcast to tasks room
        async_to_sync(channel_layer.group_send)(
            f"event_{event_slug}_tasks",
            {
                'type': 'task_update',
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
        
        logger.info(f"Task {action} broadcast sent for event {event_slug}")


@receiver(post_delete, sender=Task)
def task_deleted_signal(sender, instance, **kwargs):
    """Signal handler for when a task is deleted."""
    if channel_layer:
        # Get event slug
        event_slug = instance.event.slug
        
        # Prepare task data
        task_data = {
            'id': instance.id,
            'title': instance.title,
            'status': instance.status,
            'assigned_to': {
                'id': instance.assigned_to.id,
                'name': instance.assigned_to.name
            } if instance.assigned_to else None
        }
        
        # Prepare message data
        message_data = {
            'type': 'task_update',
            'action': 'deleted',
            'data': {
                'task': task_data,
                'timestamp': instance.updated_at.isoformat()
            }
        }
        
        # Broadcast to tasks room
        async_to_sync(channel_layer.group_send)(
            f"event_{event_slug}_tasks",
            {
                'type': 'task_update',
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
        
        logger.info(f"Task deleted broadcast sent for event {event_slug}")
