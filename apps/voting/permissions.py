from django.utils import timezone
from rest_framework import permissions

from events.models import Event, TimeSlot
from .models import Vote


class CanVoteOnTimeslot(permissions.BasePermission):
    """
    Custom permission to check if a user can vote on a timeslot.
    
    Restrictions:
    - User must be authenticated
    - Timeslot must be in the future
    - Event must not be locked
    - User cannot be the event creator (optional business rule)
    - User cannot have already voted for this timeslot
    """
    
    message = "You don't have permission to vote on this timeslot."
    
    def has_permission(self, request, view):
        """Check basic permission requirements."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Check object-level permissions for voting on a specific timeslot."""
        user = request.user
        
        # Determine the timeslot based on the object type
        if isinstance(obj, TimeSlot):
            timeslot = obj
        elif isinstance(obj, Vote):
            timeslot = obj.timeslot
        else:
            return False
        
        # Check if timeslot is in the future
        if timeslot.datetime <= timezone.now():
            self.message = "Cannot vote for past timeslots."
            return False
        
        # Check if event is locked
        if timeslot.event.status == 'locked':
            self.message = "Cannot vote on locked events."
            return False
        
        # Check if user is the event creator (business rule)
        if timeslot.event.created_by == user:
            self.message = "Event creators cannot vote on their own events."
            return False
        
        # For POST/PUT requests, check if user already voted
        if request.method in ['POST', 'PUT']:
            if Vote.objects.filter(user=user, timeslot=timeslot).exists():
                self.message = "You have already voted for this timeslot."
                return False
        
        return True


class CanViewVotingDetails(permissions.BasePermission):
    """
    Custom permission to control access to detailed voting information.
    
    Rules:
    - Authenticated users can view basic vote counts
    - Event creators can view detailed voter information
    - Staff users can view all voting details
    """
    
    def has_permission(self, request, view):
        """Check basic permission requirements."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Check object-level permissions for viewing voting details."""
        user = request.user
        
        # Staff users can view everything
        if user.is_staff or user.is_superuser:
            return True
        
        # Determine the event based on the object type
        if isinstance(obj, Event):
            event = obj
        elif isinstance(obj, TimeSlot):
            event = obj.event
        elif isinstance(obj, Vote):
            event = obj.timeslot.event
        else:
            return False
        
        # Event creators can view detailed information about their events
        if event.created_by == user:
            return True
        
        # Regular users can view basic information
        return True


class CanManageVotes(permissions.BasePermission):
    """
    Custom permission to check if a user can manage (delete) their votes.
    
    Rules:
    - Users can only delete their own votes
    - Cannot delete votes if the event is locked
    - Cannot delete votes for past timeslots
    """
    
    message = "You don't have permission to manage this vote."
    
    def has_permission(self, request, view):
        """Check basic permission requirements."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Check object-level permissions for managing votes."""
        user = request.user
        
        # Users can only manage their own votes
        if obj.user != user:
            self.message = "You can only manage your own votes."
            return False
        
        # Cannot delete votes if event is locked
        if obj.timeslot.event.status == 'locked':
            self.message = "Cannot modify votes for locked events."
            return False
        
        # Cannot delete votes for past timeslots
        if obj.timeslot.datetime <= timezone.now():
            self.message = "Cannot modify votes for past timeslots."
            return False
        
        return True


class IsEventCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow event creators to manage their events.
    
    Rules:
    - Event creators can modify their events
    - Other authenticated users can only read
    - Anonymous users get no access
    """
    
    def has_permission(self, request, view):
        """Check basic permission requirements."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Check object-level permissions."""
        user = request.user
        
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Determine the event based on the object type
        if isinstance(obj, Event):
            event = obj
        elif isinstance(obj, TimeSlot):
            event = obj.event
        else:
            return False
        
        # Write permissions only for event creator
        return event.created_by == user


class CanAccessEvent(permissions.BasePermission):
    """
    Custom permission to check if a user can access an event.
    
    For now, all authenticated users can access all events.
    This can be extended later for private events.
    """
    
    def has_permission(self, request, view):
        """Check basic permission requirements."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Check object-level permissions for accessing events."""
        # For now, all authenticated users can access all events
        return request.user and request.user.is_authenticated
