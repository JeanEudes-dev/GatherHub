"""
GatherHub Custom Permission Classes

Comprehensive permission system for fine-grained access control.
"""
import logging
from typing import Any
from django.http import HttpRequest
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger('gatherhub.security')


class IsActiveUser(BasePermission):
    """
    Only allow active users to access the API.
    """
    message = "Your account has been deactivated. Please contact support."

    def has_permission(self, request: HttpRequest, view: Any):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_active:
            user_email = getattr(request.user, 'email', str(request.user))
            logger.warning(f"Inactive user attempted API access: {user_email}")
            return False
        
        return True


class HasAPIAccess(BasePermission):
    """
    Check if user has API access (for future premium features).
    Currently allows all authenticated users.
    """
    message = "You don't have API access permissions."

    def has_permission(self, request: HttpRequest, view: Any):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Future: Check for premium subscription or API access flag
        # For now, all authenticated users have API access
        return True


class IsOwnerOrReadOnly(BasePermission):
    """
    Only allow owners to modify their resources.
    Read permissions for any authenticated user.
    """
    message = "You can only modify your own resources."

    def has_object_permission(self, request: HttpRequest, view: Any, obj: Any):  # type: ignore[override]
        # Read permissions for any authenticated user
        if request.method in SAFE_METHODS:
            return True

        # Write permissions only for the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # If no ownership field found, deny write access
        obj_id = getattr(obj, 'pk', getattr(obj, 'id', 'unknown'))
        logger.warning(f"Ownership check failed for {obj.__class__.__name__} {obj_id}")
        return False


class EventMembershipRequired(BasePermission):
    """
    Require event membership for access to event-related resources.
    """
    message = "You must be a member of this event to access this resource."

    def has_object_permission(self, request: HttpRequest, view: Any, obj: Any):  # type: ignore[override]
        user = request.user
        
        # Get the event from the object
        event = None
        if hasattr(obj, 'event'):
            event = obj.event
        elif hasattr(obj, 'timeslot') and hasattr(obj.timeslot, 'event'):
            event = obj.timeslot.event
        elif obj.__class__.__name__ == 'Event':
            event = obj
        
        if not event:
            obj_id = getattr(obj, 'pk', getattr(obj, 'id', 'unknown'))
            logger.warning(f"Could not determine event for {obj.__class__.__name__} {obj_id}")
            return False
        
        # Event owner has full access
        if event.created_by == user:
            return True
        
        # Check if user is a member
        user_id = getattr(user, 'pk', getattr(user, 'id', None))
        if hasattr(event, 'members') and user_id and event.members.filter(id=user_id).exists():
            return True
        
        # Check if user is an attendee
        if hasattr(event, 'attendees') and user_id and event.attendees.filter(id=user_id).exists():
            return True
        
        user_email = getattr(user, 'email', str(user))
        event_id = getattr(event, 'pk', getattr(event, 'id', 'unknown'))
        logger.info(f"User {user_email} denied access to event {event_id} - not a member")
        return False


class IsEventOwnerOrMember(BasePermission):
    """
    Allow event owners and members to access/modify event resources.
    """
    message = "You must be the event owner or a member to access this resource."

    def has_object_permission(self, request: HttpRequest, view: Any, obj: Any):  # type: ignore[override]
        user = request.user
        
        # Get the event
        event = getattr(obj, 'event', obj)
        
        # Event owner has full access
        if event.created_by == user:
            return True
        
        # Members have read access, limited write access
        user_id = getattr(user, 'pk', getattr(user, 'id', None))
        if hasattr(event, 'members') and user_id and event.members.filter(id=user_id).exists():
            # Define which actions members can perform
            allowed_actions = ['list', 'retrieve', 'create']
            view_action = getattr(view, 'action', None)
            if view_action in allowed_actions:
                return True
            
            # For specific write operations, check if user owns the specific object
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return self._is_object_owner(obj, user)
        
        return False
    
    def _is_object_owner(self, obj: Any, user: Any) -> bool:
        """Check if user owns the specific object."""
        owner_fields = ['user', 'created_by', 'assigned_to', 'voter']
        for field in owner_fields:
            if hasattr(obj, field) and getattr(obj, field) == user:
                return True
        return False


class IsTaskAssigneeOrEventOwner(BasePermission):
    """
    Allow task assignees and event owners to modify tasks.
    """
    message = "You can only modify tasks assigned to you or tasks in events you own."

    def has_object_permission(self, request: HttpRequest, view: Any, obj: Any):  # type: ignore[override]
        user = request.user
        
        # Task assignee can modify their tasks
        if hasattr(obj, 'assigned_to') and obj.assigned_to == user:
            return True
        
        # Event owner can modify all tasks
        if hasattr(obj, 'event') and obj.event.created_by == user:
            return True
        
        # Task creator can modify their tasks
        if hasattr(obj, 'created_by') and obj.created_by == user:
            return True
        
        return False


class CanVotePermission(BasePermission):
    """
    Permission to check if user can vote on a timeslot.
    """
    message = "You don't have permission to vote on this timeslot."

    def has_object_permission(self, request: HttpRequest, view: Any, obj: Any):  # type: ignore[override]
        user = request.user
        
        # Get the timeslot and event
        if hasattr(obj, 'timeslot'):
            timeslot = obj.timeslot
            event = timeslot.event
        elif hasattr(obj, 'event'):
            event = obj.event
            timeslot = obj
        else:
            return False
        
        # Check if event allows voting
        if hasattr(event, 'voting_enabled') and not event.voting_enabled:
            return False
        
        # Check if voting period is active
        if hasattr(event, 'voting_deadline') and event.voting_deadline:
            from django.utils import timezone
            if timezone.now() > event.voting_deadline:
                return False
        
        # Event members can vote
        user_id = getattr(user, 'pk', getattr(user, 'id', None))
        if user_id and event.members.filter(id=user_id).exists():
            return True
        
        # Event attendees can vote
        if hasattr(event, 'attendees') and user_id and event.attendees.filter(id=user_id).exists():
            return True
        
        # Event owner can vote
        if event.created_by == user:
            return True
        
        return False


class AdminOrReadOnly(BasePermission):
    """
    Allow admin users full access, others read-only.
    """
    message = "You need admin privileges to modify this resource."

    def has_permission(self, request: HttpRequest, view: Any):  # type: ignore[override]
        if request.method in SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class IsSuperUserOrReadOnly(BasePermission):
    """
    Allow superusers full access, others read-only.
    """
    message = "You need superuser privileges to modify this resource."

    def has_permission(self, request: HttpRequest, view: Any):  # type: ignore[override]
        if request.method in SAFE_METHODS:
            return True
        
        return request.user and request.user.is_superuser
