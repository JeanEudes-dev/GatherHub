"""
Task-specific WebSocket consumer for real-time task updates.
"""

import json
import logging
from channels.db import database_sync_to_async
from .base import BaseConsumer

logger = logging.getLogger(__name__)


class TasksConsumer(BaseConsumer):
    """WebSocket consumer for task updates."""
    
    async def get_room_group_name(self):
        """Get the tasks room group name."""
        return f"event_{self.event_slug}_tasks"
    
    @database_sync_to_async
    def check_event_access(self):
        """Check if user can access the event for task management."""
        from apps.events.models import Event
        try:
            event = Event.objects.get(slug=self.event_slug)
            # Allow access to both draft and locked events for task management
            return True
        except Event.DoesNotExist:
            return False
    
    async def connect(self):
        """Handle WebSocket connection for tasks."""
        await super().connect()
        
        if self.user:
            # Send current tasks data on connection
            tasks_data = await self.get_tasks_data()
            if tasks_data:
                await self.send_json({
                    'type': 'tasks_data',
                    'data': tasks_data
                })
    
    @database_sync_to_async
    def get_tasks_data(self):
        """Get current tasks data for the event."""
        from apps.events.models import Event
        from apps.tasks.models import Task
        
        try:
            event = Event.objects.get(slug=self.event_slug)
            tasks = Task.objects.filter(event=event).select_related('assigned_to')
            
            tasks_data = []
            for task in tasks:
                task_data = {
                    'id': task.pk,  # Use the primary key field
                    'title': task.title,
                    'status': task.status,
                    'assigned_to': None,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat()
                }
                
                if task.assigned_to:
                    task_data['assigned_to'] = {
                        'id': task.assigned_to.id,
                        'first_name': task.assigned_to.first_name,
                        'last_name': task.assigned_to.last_name,
                        'email': task.assigned_to.email
                    }
                
                tasks_data.append(task_data)
            
            return {
                'event_slug': self.event_slug,
                'event_status': event.status,
                'tasks': tasks_data
            }
        except Event.DoesNotExist:
            return None
    
    # Message handlers
    async def handle_task_create(self, data):
        """Handle task creation request."""
        title = data.get('title', '').strip()
        if not title:
            await self.send_error('Missing task title')
            return
        
        result = await self.create_task(title)
        if result:
            await self.send_json({
                'type': 'task_created',
                'data': result
            })
        else:
            await self.send_error('Failed to create task')
    
    async def handle_task_update(self, data):
        """Handle task update request."""
        task_id = data.get('task_id')
        if not task_id:
            await self.send_error('Missing task_id')
            return
        
        updates = data.get('updates', {})
        result = await self.update_task(task_id, updates)
        if result:
            await self.send_json({
                'type': 'task_updated',
                'data': result
            })
        else:
            await self.send_error('Failed to update task')
    
    async def handle_task_delete(self, data):
        """Handle task deletion request."""
        task_id = data.get('task_id')
        if not task_id:
            await self.send_error('Missing task_id')
            return
        
        result = await self.delete_task(task_id)
        if result:
            await self.send_json({
                'type': 'task_deleted',
                'data': result
            })
        else:
            await self.send_error('Failed to delete task')
    
    @database_sync_to_async
    def create_task(self, title):
        """Create a new task."""
        from apps.events.models import Event
        from apps.tasks.models import Task
        
        try:
            event = Event.objects.get(slug=self.event_slug)
            
            task = Task.objects.create(
                event=event,
                title=title,
                status='todo'
            )
            
            return {
                'task': {
                    'id': task.pk,
                    'title': task.title,
                    'status': task.status,
                    'assigned_to': None
                },
                'created_by': {
                    'id': self.user.id, # type: ignore
                    'first_name': self.user.first_name, # type: ignore
                    'last_name': self.user.last_name # type: ignore
                },
                'timestamp': self.get_timestamp()
            }
            
        except Event.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_task(self, task_id, updates):
        """Update an existing task."""
        from apps.tasks.models import Task
        from apps.accounts.models import CustomUser
        
        try:
            task = Task.objects.select_related('assigned_to').get(
                id=task_id,
                event__slug=self.event_slug
            )
            
            changes = {}
            
            # Handle status change
            if 'status' in updates and updates['status'] in ['todo', 'doing', 'done']:
                old_status = task.status
                task.status = updates['status']
                changes['status'] = {'from': old_status, 'to': task.status}
            
            # Handle assignment change
            if 'assigned_to_id' in updates:
                old_assigned = task.assigned_to
                if updates['assigned_to_id']:
                    try:
                        new_assignee = CustomUser.objects.get(id=updates['assigned_to_id'])
                        task.assigned_to = new_assignee
                    except CustomUser.DoesNotExist:
                        return None
                else:
                    task.assigned_to = None
                
                changes['assigned_to'] = {
                    'from': {
                        'id': old_assigned.id,
                        'first_name': old_assigned.first_name,
                        'last_name': old_assigned.last_name
                    } if old_assigned else None,
                    'to': {
                        'id': task.assigned_to.id, # type: ignore
                        'first_name': task.assigned_to.first_name, # type: ignore
                        'last_name': task.assigned_to.last_name # type: ignore
                    } if task.assigned_to else None
                }
            
            # Handle title change
            if 'title' in updates and updates['title'].strip():
                old_title = task.title
                task.title = updates['title'].strip()
                changes['title'] = {'from': old_title, 'to': task.title}
            
            task.save()
            
            return {
                'task': {
                    'id': task.id, # type: ignore
                    'title': task.title,
                    'status': task.status,
                    'assigned_to': {
                        'id': task.assigned_to.id,
                        'first_name': task.assigned_to.first_name,
                        'last_name': task.assigned_to.last_name
                    } if task.assigned_to else None
                },
                'changed_by': {
                    'id': self.user.id, # type: ignore
                    'first_name': self.user.first_name, # type: ignore
                    'last_name': self.user.last_name # type: ignore
                },
                'changes': changes,
                'timestamp': self.get_timestamp()
            }
            
        except Task.DoesNotExist:
            return None
    
    @database_sync_to_async
    def delete_task(self, task_id):
        """Delete a task."""
        from apps.tasks.models import Task
        
        try:
            task = Task.objects.get(
                id=task_id,
                event__slug=self.event_slug
            )
            
            task_data = {
                'task': {
                    'id': task.id, # type: ignore
                    'title': task.title,
                    'status': task.status,
                    'assigned_to': {
                        'id': task.assigned_to.id,
                        'first_name': task.assigned_to.first_name,
                        'last_name': task.assigned_to.last_name
                    } if task.assigned_to else None
                },
                'deleted_by': {
                    'id': self.user.id, # type: ignore
                    'first_name': self.user.first_name, # type: ignore
                    'last_name': self.user.last_name # type: ignore
                },
                'timestamp': self.get_timestamp()
            }
            
            task.delete()
            return task_data
            
        except Task.DoesNotExist:
            return None
    
    # Broadcast handlers for group messages
    async def task_update(self, event):
        """Handle task update broadcasts."""
        await self.send_json(event['message'])
