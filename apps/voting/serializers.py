from typing import Any, Optional, Dict, List
from django.utils import timezone
from rest_framework import serializers
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema_field

from apps.accounts.models import CustomUser
from apps.events.models import Event, TimeSlot
from .models import Vote


class UserVoteSerializer(serializers.ModelSerializer):
    """Serializer for user information in votes."""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email']
        read_only_fields = ['id', 'name', 'email']


class TimeslotBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for timeslot information in votes."""
    
    event = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'datetime', 'event']
        read_only_fields = ['id', 'datetime']
    
    @extend_schema_field(serializers.DictField)
    def get_event(self, obj: TimeSlot) -> Dict[str, Any]:
        """Get basic event information."""
        return {
            'id': obj.event.pk,
            'title': obj.event.title,
            'slug': obj.event.slug,
            'status': obj.event.status
        }


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for vote display with user and timeslot info."""
    
    user = UserVoteSerializer(read_only=True)
    timeslot = TimeslotBasicSerializer(read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'user', 'timeslot', 'created_at']
        read_only_fields = ['id', 'user', 'timeslot', 'created_at']


class VoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating votes with validation."""
    
    timeslot = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all()
    )
    
    class Meta:
        model = Vote
        fields = ['timeslot']
    
    def validate_timeslot(self, value: TimeSlot) -> TimeSlot:
        """Validate timeslot voting conditions."""
        user = self.context['request'].user
        
        # Check if timeslot is in the future
        if value.datetime <= timezone.now():
            raise serializers.ValidationError("Cannot vote for past timeslots.")
        
        # Check if event is locked
        if value.event.status == 'locked':
            raise serializers.ValidationError("Cannot vote on locked events.")
        
        # Check if user is the event creator (optional business rule)
        if value.event.created_by == user:
            raise serializers.ValidationError("Event creators cannot vote on their own events.")
        
        return value
    
    def validate(self, attrs):
        """Additional validation for vote creation."""
        user = self.context['request'].user
        timeslot = attrs['timeslot']
        
        # Check if user already voted for this timeslot
        if Vote.objects.filter(user=user, timeslot=timeslot).exists():
            raise serializers.ValidationError("You have already voted for this timeslot.")
        
        return attrs
    
    def create(self, validated_data):
        """Create vote with authenticated user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TimeslotVoteSummarySerializer(serializers.Serializer):
    """Serializer for displaying vote counts and voter lists for a timeslot."""
    
    timeslot_id = serializers.IntegerField()
    datetime = serializers.DateTimeField()
    vote_count = serializers.IntegerField()
    user_voted = serializers.BooleanField()
    can_vote = serializers.BooleanField()
    voters = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of voter emails (optional based on privacy settings)"
    )
    
    def to_representation(self, instance: TimeSlot) -> Dict[str, Any]:
        """Convert timeslot instance to summary representation."""
        request = self.context.get('request')
        user: Optional[CustomUser] = request.user if request and hasattr(request, 'user') else None
        include_voters = self.context.get('include_voters', False)
        
        # Get vote count - using type: ignore for Django's dynamic attributes
        vote_count = instance.votes.count()  # type: ignore[attr-defined]
        
        # Check if current user voted
        user_voted = False
        if user and user.is_authenticated:
            user_voted = instance.votes.filter(user=user).exists()  # type: ignore[attr-defined]
        
        # Check if user can vote
        can_vote = False
        if user and user.is_authenticated:
            can_vote = (
                instance.datetime > timezone.now() and
                instance.event.status != 'locked' and
                instance.event.created_by != user and
                not user_voted
            )
        
        data = {
            'timeslot_id': instance.pk,
            'datetime': instance.datetime,
            'vote_count': vote_count,
            'user_voted': user_voted,
            'can_vote': can_vote,
        }
        
        # Include voter list if requested
        if include_voters:
            voters = instance.votes.select_related('user').values_list('user__email', flat=True)  # type: ignore[attr-defined]
            data['voters'] = list(voters)
        
        return data


class EventVotingSummarySerializer(serializers.Serializer):
    """Serializer for showing voting status across all event timeslots."""
    
    event = serializers.SerializerMethodField()
    timeslots = serializers.SerializerMethodField()
    total_votes = serializers.IntegerField()
    most_popular_timeslot = serializers.SerializerMethodField()
    participation_stats = serializers.SerializerMethodField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_instance = kwargs.get('instance')
    
    @extend_schema_field(serializers.DictField)
    def get_event(self, obj: Event) -> Dict[str, Any]:
        """Get basic event information."""
        return {
            'id': obj.pk,
            'title': obj.title,
            'slug': obj.slug,
            'status': obj.status,
            'created_by': {
                'id': obj.created_by.pk,
                'name': obj.created_by.name,
                'email': obj.created_by.email
            }
        }
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_timeslots(self, obj: Event) -> List[Dict[str, Any]]:
        """Get voting summary for each timeslot."""
        request = self.context.get('request')
        user: Optional[CustomUser] = request.user if request and hasattr(request, 'user') else None
        timeslots_data = []
        
        for timeslot in obj.time_slots.prefetch_related('votes__user').all():  # type: ignore[attr-defined]
            vote_count = timeslot.votes.count()  # type: ignore[attr-defined]
            user_voted = False
            
            if user and user.is_authenticated:
                user_voted = timeslot.votes.filter(user=user).exists()  # type: ignore[attr-defined]
            
            timeslots_data.append({
                'id': timeslot.pk,
                'datetime': timeslot.datetime,
                'vote_count': vote_count,
                'user_voted': user_voted
            })
        
        return timeslots_data
    
    @extend_schema_field(serializers.DictField)
    def get_most_popular_timeslot(self, obj: Event) -> Optional[Dict[str, Any]]:
        """Get the timeslot with the most votes."""
        timeslots_with_votes = []
        
        for timeslot in obj.time_slots.prefetch_related('votes').all():  # type: ignore[attr-defined]
            vote_count = timeslot.votes.count()  # type: ignore[attr-defined]
            timeslots_with_votes.append((timeslot, vote_count))
        
        if not timeslots_with_votes:
            return None
        
        # Sort by vote count (descending)
        timeslots_with_votes.sort(key=lambda x: x[1], reverse=True)
        most_popular = timeslots_with_votes[0]
        
        if most_popular[1] == 0:  # No votes yet
            return None
        
        return {
            'id': most_popular[0].pk,
            'datetime': most_popular[0].datetime,
            'vote_count': most_popular[1]
        }
    
    @extend_schema_field(serializers.DictField)
    def get_participation_stats(self, obj: Event) -> Dict[str, Any]:
        """Get participation statistics."""
        total_timeslots = obj.time_slots.count()  # type: ignore[attr-defined]
        total_votes = sum(ts.votes.count() for ts in obj.time_slots.prefetch_related('votes').all())  # type: ignore[attr-defined]
        unique_voters = Vote.objects.filter(
            timeslot__event=obj
        ).values('user').distinct().count()
        
        return {
            'total_timeslots': total_timeslots,
            'total_votes': total_votes,
            'unique_voters': unique_voters,
            'avg_votes_per_timeslot': round(total_votes / total_timeslots, 2) if total_timeslots > 0 else 0
        }
    
    def to_representation(self, instance: Event) -> Dict[str, Any]:
        """Convert event instance to voting summary representation."""
        # Calculate total votes across all timeslots
        total_votes = sum(ts.votes.count() for ts in instance.time_slots.prefetch_related('votes').all())  # type: ignore[attr-defined]
        
        return {
            'event': self.get_event(instance),
            'timeslots': self.get_timeslots(instance),
            'total_votes': total_votes,
            'most_popular_timeslot': self.get_most_popular_timeslot(instance),
            'participation_stats': self.get_participation_stats(instance)
        }


class BulkVoteSerializer(serializers.Serializer):
    """Serializer for bulk voting on multiple timeslots."""
    
    timeslot_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of timeslot IDs to vote for"
    )
    
    def validate_timeslot_ids(self, value: List[int]) -> List[int]:
        """Validate that all timeslot IDs exist and belong to the same event."""
        user = self.context['request'].user
        event_slug = self.context.get('event_slug')
        
        if not event_slug:
            raise serializers.ValidationError("Event context is required.")
        
        try:
            event = Event.objects.get(slug=event_slug)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
        
        # Get all timeslots for validation
        timeslots = TimeSlot.objects.filter(
            id__in=value,
            event=event
        ).select_related('event')
        
        if len(timeslots) != len(value):
            raise serializers.ValidationError("Some timeslot IDs are invalid or don't belong to this event.")
        
        # Validate each timeslot
        for timeslot in timeslots:
            # Check if timeslot is in the future
            if timeslot.datetime <= timezone.now():
                raise serializers.ValidationError(f"Cannot vote for past timeslot: {timeslot.pk}")
            
            # Check if event is locked
            if timeslot.event.status == 'locked':
                raise serializers.ValidationError("Cannot vote on locked events.")
            
            # Check if user is the event creator
            if timeslot.event.created_by == user:
                raise serializers.ValidationError("Event creators cannot vote on their own events.")
        
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create votes for multiple timeslots."""
        user = self.context['request'].user
        event_slug = self.context['event_slug']
        timeslot_ids = validated_data['timeslot_ids']
        
        event = Event.objects.get(slug=event_slug)
        timeslots = TimeSlot.objects.filter(id__in=timeslot_ids, event=event)
        
        # Get existing votes to avoid duplicates
        existing_votes = Vote.objects.filter(
            user=user,
            timeslot__in=timeslots
        ).values_list('timeslot_id', flat=True)
        
        # Create votes for timeslots that don't have votes yet
        votes_to_create = []
        for timeslot in timeslots:
            if timeslot.pk not in existing_votes:
                votes_to_create.append(Vote(user=user, timeslot=timeslot))
        
        created_votes = Vote.objects.bulk_create(votes_to_create)
        
        return {
            'created_votes': len(created_votes),
            'skipped_existing': len(existing_votes),
            'total_requested': len(timeslot_ids)
        }
