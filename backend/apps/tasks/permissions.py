from rest_framework import permissions
from apps.events.models import Event


class IsEventMember(permissions.BasePermission):
    """
    Custom permission to only allow event members to view tasks.
    Event members are: event creator or users who have voted on the event.
    """

    def has_object_permission(self, request, view, obj): # type: ignore
        # Get the event from the task
        event = obj.event
        user = request.user
        
        # Check if user is authenticated
        if not user.is_authenticated:
            return False
        
        # Event creator can always access
        if event.created_by == user:
            return True
        
        # Check if user has voted on any timeslot of this event
        if user.votes.filter(timeslot__event=event).exists():
            return True
        
        return False


class IsTaskAssigneeOrEventCreator(permissions.BasePermission):
    """
    Custom permission to only allow task assignee or event creator to update/delete tasks.
    """

    def has_object_permission(self, request, view, obj): # type: ignore
        # Read permissions are allowed to event members (handled by IsEventMember)
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        
        # Check if user is authenticated
        if not user.is_authenticated:
            return False
        
        # Event creator can always modify
        if obj.event.created_by == user:
            return True
        
        # Assigned user can update status but not reassign
        if obj.assigned_to == user:
            # For updates, check if they're only changing status
            if request.method in ['PUT', 'PATCH']:
                # This will be further validated in the serializer
                return True
            # Assigned user cannot delete tasks
            return False
        
        return False


class CanAssignTasks(permissions.BasePermission):
    """
    Custom permission to only allow event creators to assign/reassign tasks.
    """

    def has_object_permission(self, request, view, obj): # type: ignore
        # Only apply this to assignment operations
        if request.method not in ['PUT', 'PATCH']:
            return True
        
        user = request.user
        
        # Check if user is authenticated
        if not user.is_authenticated:
            return False
        
        # Only event creator can assign/reassign tasks
        if obj.event.created_by == user:
            return True
        
        # If assigned user is trying to update, check if they're only changing status
        if obj.assigned_to == user:
            # Check if the request is only updating status (not assignment)
            data = getattr(request, 'data', {})
            if 'assigned_to' in data and data['assigned_to'] != obj.assigned_to.id:
                return False  # Cannot reassign
            return True
        
        return False


class CanModifyTask(permissions.BasePermission):
    """
    Custom permission to prevent editing tasks for locked events.
    """

    def has_object_permission(self, request, view, obj): # type: ignore
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check if parent event is not locked
        # Allow deletion even for locked events (creator decision)
        if request.method == 'DELETE':
            return obj.event.created_by == request.user
            
        # For updates, prevent modification of locked events except status updates by assignee
        if obj.event.status == 'locked':
            # Only assigned user can update status of their tasks in locked events
            if obj.assigned_to == request.user:
                data = getattr(request, 'data', {})
                # Only allow status updates, not other changes
                allowed_fields = {'status'}
                request_fields = set(data.keys())
                return request_fields.issubset(allowed_fields)
            return False
            
        return True


class IsEventCreatorForTaskCreation(permissions.BasePermission):
    """
    Custom permission for task creation - only event members can create tasks.
    """

    def has_permission(self, request, view): # type: ignore
        # For list view, allow authenticated users
        if request.method == 'GET':
            return request.user.is_authenticated
        
        # For creation, check if user is associated with the event
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return False
            
            # Get event from request data or URL
            event_id = request.data.get('event')
            event_slug = view.kwargs.get('event_slug')
            
            if event_slug:
                # Creating via event-specific endpoint
                try:
                    event = Event.objects.get(slug=event_slug)
                    user = request.user
                    
                    # Check if user is event creator or has voted
                    if (event.created_by == user or 
                        user.votes.filter(timeslot__event=event).exists()):
                        return True
                except Event.DoesNotExist:
                    return False
            elif event_id:
                # Creating via general endpoint
                try:
                    event = Event.objects.get(id=event_id)
                    user = request.user
                    
                    # Check if user is event creator or has voted
                    if (event.created_by == user or 
                        user.votes.filter(timeslot__event=event).exists()):
                        return True
                except Event.DoesNotExist:
                    return False
            
            return False
        
        return True
