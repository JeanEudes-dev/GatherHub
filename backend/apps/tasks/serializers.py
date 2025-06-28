from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task
from apps.events.models import Event

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for task assignments."""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class EventBasicSerializer(serializers.ModelSerializer):
    """Basic event serializer for task display."""
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'slug']


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer for display with related data."""
    
    assigned_to = UserBasicSerializer(read_only=True)
    event = EventBasicSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'assigned_to', 'event',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new tasks."""
    
    class Meta:
        model = Task
        fields = ['title', 'event', 'assigned_to']
        
    def validate_event(self, value):
        """Validate that the event exists and is not locked."""
        if value.status == 'locked':
            raise serializers.ValidationError(
                "Cannot create tasks for locked events."
            )
        return value
    
    def validate_assigned_to(self, value):
        """Validate that assigned user is associated with the event."""
        if value and hasattr(self, 'initial_data') and self.initial_data:
            event_id = self.initial_data.get('event') if isinstance(self.initial_data, dict) else None
            if event_id:
                try:
                    event = Event.objects.get(id=event_id)
                    # Check if user is event creator or has voted (is a participant)
                    if not (value == event.created_by or 
                           value.votes.filter(timeslot__event=event).exists()):
                        raise serializers.ValidationError(
                            "Cannot assign task to user not associated with this event."
                        )
                except Event.DoesNotExist:
                    pass  # Let event validation handle this
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating task status and assignment."""
    
    VALID_STATUS_TRANSITIONS = {
        'todo': ['doing', 'done'],
        'doing': ['todo', 'done'],
        'done': ['doing']
    }
    
    class Meta:
        model = Task
        fields = ['title', 'status', 'assigned_to']
        
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance and self.instance.status != value:
            current_status = self.instance.status
            valid_transitions = self.VALID_STATUS_TRANSITIONS.get(current_status, [])
            if value not in valid_transitions and value != current_status:
                raise serializers.ValidationError(
                    f"Invalid status transition from '{current_status}' to '{value}'. "
                    f"Valid transitions: {valid_transitions}"
                )
        return value
    
    def validate_assigned_to(self, value):
        """Validate that assigned user is associated with the event."""
        if value and self.instance:
            event = self.instance.event
            # Check if user is event creator or has voted (is a participant)
            if not (value == event.created_by or 
                   value.votes.filter(timeslot__event=event).exists()):
                raise serializers.ValidationError(
                    "Cannot assign task to user not associated with this event."
                )
        return value
    
    def validate(self, attrs):
        """Validate that locked events cannot be modified."""
        if self.instance and self.instance.event.status == 'locked':
            # Only allow status updates by assigned user, not reassignment
            if 'assigned_to' in attrs and attrs['assigned_to'] != self.instance.assigned_to:
                raise serializers.ValidationError(
                    "Cannot reassign tasks for locked events."
                )
        return attrs


class TaskStatusHistorySerializer(serializers.Serializer):
    """Serializer for task status history (for future implementation)."""
    
    status = serializers.CharField()
    changed_at = serializers.DateTimeField()
    changed_by = UserBasicSerializer()
    previous_status = serializers.CharField()


class TaskEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks within a specific event context."""
    
    class Meta:
        model = Task
        fields = ['title', 'assigned_to']
    
    def validate_assigned_to(self, value):
        """Validate that assigned user is associated with the event."""
        if value:
            # Event will be set in the view based on the URL
            event = self.context.get('event')
            if event:
                # Check if user is event creator or has voted (is a participant)
                if not (value == event.created_by or 
                       value.votes.filter(timeslot__event=event).exists()):
                    raise serializers.ValidationError(
                        "Cannot assign task to user not associated with this event."
                    )
        return value
