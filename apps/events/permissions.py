from rest_framework import permissions


class IsEventCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an event to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the event.
        return obj.created_by == request.user


class CanModifyEventContent(permissions.BasePermission):
    """
    Custom permission to prevent editing locked events.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check if event is not locked
        # Allow deletion even for locked events (creator decision)
        if request.method == 'DELETE':
            return True
            
        # For updates, prevent modification of locked events
        return obj.status != 'locked'


class CanModifyTimeSlot(permissions.BasePermission):
    """
    Custom permission to prevent editing timeslots for locked events.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check if parent event is not locked
        return obj.event.status != 'locked'
