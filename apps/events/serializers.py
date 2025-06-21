from typing import Any
import markdown
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_spectacular.utils import extend_schema_field

from accounts.models import CustomUser
from .models import Event, TimeSlot


class UserSummarySerializer(serializers.ModelSerializer):
    """Serializer for user summary information."""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot model with vote count integration."""
    
    vote_count = serializers.SerializerMethodField()
    user_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'datetime', 'vote_count', 'user_voted', 'created_at']
        read_only_fields = ['created_at']
    
    @extend_schema_field(serializers.IntegerField)
    def get_vote_count(self, obj: TimeSlot) -> int:
        """Get actual vote count for the timeslot."""
        # Use prefetch_related if available, otherwise query
        if hasattr(obj, '_prefetched_objects_cache') and 'votes' in getattr(obj, '_prefetched_objects_cache', {}):  # type: ignore[attr-defined]
            return len(getattr(obj, '_prefetched_objects_cache')['votes'])  # type: ignore[attr-defined]
        return obj.votes.count()  # type: ignore[attr-defined]
    
    @extend_schema_field(serializers.BooleanField)
    def get_user_voted(self, obj: TimeSlot) -> bool:
        """Check if the current user has voted for this timeslot."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Use prefetch_related if available for performance
        if hasattr(obj, '_prefetched_objects_cache') and 'votes' in getattr(obj, '_prefetched_objects_cache', {}):  # type: ignore[attr-defined]
            user_votes = [vote for vote in getattr(obj, '_prefetched_objects_cache')['votes'] if vote.user_id == request.user.id]  # type: ignore[attr-defined]
            return len(user_votes) > 0
        
        return obj.votes.filter(user=request.user).exists()  # type: ignore[attr-defined]
    
    def validate_datetime(self, value):
        """Validate that datetime is in the future."""
        if value <= timezone.now():
            raise serializers.ValidationError("Datetime must be in the future.")
        return value
    
    def validate(self, attrs):
        """Validate that the parent event is not locked."""
        if self.instance and self.instance.event.status == 'locked':
            raise serializers.ValidationError("Cannot modify timeslots for locked events.")
        return attrs


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for event listing with summary data."""
    
    created_by = UserSummarySerializer(read_only=True)
    timeslot_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'status', 'created_by', 
            'timeslot_count', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']
    
    @extend_schema_field(serializers.IntegerField)
    def get_timeslot_count(self, obj: Event) -> int:
        """Get the number of timeslots for this event."""
        return obj.time_slots.count()  # type: ignore[attr-defined]


class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed event view with all timeslots."""
    
    created_by = UserSummarySerializer(read_only=True)
    timeslots = TimeSlotSerializer(source='time_slots', many=True, read_only=True)
    description_html = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'description_html', 'slug', 
            'status', 'created_by', 'timeslots', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.CharField)
    def get_description_html(self, obj: Event) -> str:
        """Convert Markdown description to HTML."""
        if obj.description:
            return markdown.markdown(obj.description, extensions=['markdown.extensions.extra'])
        return ""


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for event creation with validation."""
    
    timeslots = TimeSlotSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'timeslots', 'slug']
        read_only_fields = ['slug']
        
    def validate_title(self, value):
        """Validate title uniqueness per user."""
        user = self.context['request'].user
        if Event.objects.filter(title=value, created_by=user).exists():
            raise serializers.ValidationError("You already have an event with this title.")
        return value
    
    def create(self, validated_data):
        """Create event with timeslots."""
        timeslots_data = validated_data.pop('timeslots', [])
        validated_data['created_by'] = self.context['request'].user
        
        # Generate unique slug
        base_slug = slugify(validated_data['title'])
        slug = base_slug
        counter = 1
        while Event.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data['slug'] = slug
        
        event = Event.objects.create(**validated_data)
        
        # Create timeslots
        for timeslot_data in timeslots_data:
            TimeSlot.objects.create(event=event, **timeslot_data)
        
        return event


class EventUpdateSerializer(serializers.ModelSerializer):
    """Serializer for event updates (only by creator)."""
    
    class Meta:
        model = Event
        fields = ['title', 'description']
    
    def validate_title(self, value):
        """Validate title uniqueness per user (excluding current instance)."""
        user = self.context['request'].user
        existing_event = Event.objects.filter(
            title=value, 
            created_by=user
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if existing_event.exists():
            raise serializers.ValidationError("You already have an event with this title.")
        return value
    
    def validate(self, attrs):
        """Validate that the event is not locked."""
        if self.instance and self.instance.status == 'locked':
            raise serializers.ValidationError("Cannot modify locked events.")
        return attrs
    
    def update(self, instance, validated_data):
        """Update event and regenerate slug if title changed."""
        if 'title' in validated_data and validated_data['title'] != instance.title:
            # Generate new unique slug
            base_slug = slugify(validated_data['title'])
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance.slug = slug
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class EventLockSerializer(serializers.Serializer):
    """Serializer for locking events."""
    
    def validate(self, attrs):
        """Validate that the event can be locked."""
        event = self.context['event']
        
        if event.status == 'locked':
            raise serializers.ValidationError("Event is already locked.")
        
        if not event.time_slots.exists():
            raise serializers.ValidationError("Cannot lock event without timeslots.")
        
        return attrs
    
    def save(self, **kwargs):
        """Lock the event."""
        event = self.context['event']
        event.status = 'locked'
        event.save()
        return event
