from typing import Any, Type
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

from events.models import Event, TimeSlot
from .models import Vote
from .serializers import (
    VoteSerializer,
    VoteCreateSerializer,
    TimeslotVoteSummarySerializer,
    EventVotingSummarySerializer,
    BulkVoteSerializer
)
from .permissions import (
    CanVoteOnTimeslot,
    CanViewVotingDetails,
    CanManageVotes,
    CanAccessEvent
)


@extend_schema_view(
    list=extend_schema(
        summary="List user's votes",
        description="Get a list of all votes made by the current user across all events."
    ),
    create=extend_schema(
        summary="Create a vote",
        description="Vote for a specific timeslot. Users can only vote once per timeslot."
    ),
    destroy=extend_schema(
        summary="Remove a vote",
        description="Remove a vote for a timeslot. Users can only remove their own votes."
    )
)
class VoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user votes.
    
    Provides endpoints for:
    - Listing current user's votes
    - Creating new votes
    - Removing existing votes
    """
    
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):  # type: ignore[override]
        """Return votes for the current user only."""
        return Vote.objects.filter(user=self.request.user).select_related(
            'timeslot__event',
            'user'
        ).order_by('-created_at')
    
    def get_serializer_class(self) -> Type[BaseSerializer]:  # type: ignore[override]
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return VoteCreateSerializer
        return VoteSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action == 'destroy':
            return [CanManageVotes()]
        elif self.action == 'create':
            return [CanVoteOnTimeslot()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Create vote with current user."""
        serializer.save(user=self.request.user)


@extend_schema_view(
    vote=extend_schema(
        summary="Vote for timeslot",
        description="Vote for a specific timeslot. If already voted, this will remove the vote (toggle)."
    ),
    unvote=extend_schema(
        summary="Remove vote from timeslot",
        description="Remove vote from a specific timeslot."
    ),
    summary=extend_schema(
        summary="Get voting summary for timeslot",
        description="Get detailed voting information for a specific timeslot including vote count and voter list."
    )
)
class TimeslotVotingViewSet(viewsets.GenericViewSet):
    """
    ViewSet for timeslot-specific voting operations.
    
    Provides endpoints for:
    - Voting/unvoting for specific timeslots
    - Getting voting summaries for timeslots
    """
    
    queryset = TimeSlot.objects.all()
    permission_classes = [IsAuthenticated, CanAccessEvent]
    
    def get_object(self) -> TimeSlot:  # type: ignore[override]
        """Get timeslot by ID."""
        return get_object_or_404(
            TimeSlot.objects.select_related('event__created_by').prefetch_related('votes__user'),
            pk=self.kwargs['pk']
        )
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[CanVoteOnTimeslot])
    def vote(self, request, pk=None):
        """
        Toggle vote for a timeslot.
        
        POST: Add vote if not already voted, remove if already voted
        DELETE: Remove vote if exists
        """
        timeslot = self.get_object()
        user = request.user
        
        existing_vote = Vote.objects.filter(user=user, timeslot=timeslot).first()
        
        if request.method == 'POST':
            if existing_vote:
                # User already voted, remove the vote (toggle)
                existing_vote.delete()
                return Response({
                    'message': 'Vote removed',
                    'voted': False,
                    'vote_count': timeslot.votes.count()  # type: ignore[attr-defined]
                }, status=status.HTTP_200_OK)
            else:
                # Create new vote
                Vote.objects.create(user=user, timeslot=timeslot)
                return Response({
                    'message': 'Vote added',
                    'voted': True,
                    'vote_count': timeslot.votes.count()  # type: ignore[attr-defined]
                }, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            if existing_vote:
                existing_vote.delete()
                return Response({
                    'message': 'Vote removed',
                    'voted': False,
                    'vote_count': timeslot.votes.count()  # type: ignore[attr-defined]
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'No vote found to remove'
                }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[CanViewVotingDetails])
    def summary(self, request, pk=None):
        """Get detailed voting summary for a timeslot."""
        timeslot = self.get_object()
        
        # Check if user is event creator to include voter details
        include_voters = (
            request.user.is_staff or 
            request.user.is_superuser or 
            timeslot.event.created_by == request.user
        )
        
        serializer = TimeslotVoteSummarySerializer(
            timeslot,
            context={
                'request': request,
                'include_voters': include_voters
            }
        )
        return Response(serializer.data)


@extend_schema_view(
    summary=extend_schema(
        summary="Get event voting summary",
        description="Get comprehensive voting statistics for all timeslots in an event."
    ),
    bulk_vote=extend_schema(
        summary="Bulk vote for multiple timeslots",
        description="Vote for multiple timeslots in an event at once."
    )
)
class EventVotingViewSet(viewsets.GenericViewSet):
    """
    ViewSet for event-level voting operations.
    
    Provides endpoints for:
    - Getting event voting summaries
    - Bulk voting for multiple timeslots
    """
    
    queryset = Event.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated, CanAccessEvent]
    
    def get_object(self) -> Event:  # type: ignore[override]
        """Get event by slug."""
        return get_object_or_404(
            Event.objects.select_related('created_by').prefetch_related(
                'time_slots__votes__user'
            ),
            slug=self.kwargs['slug']
        )
    
    @action(detail=True, methods=['get'], permission_classes=[CanViewVotingDetails])
    def summary(self, request, slug=None):
        """Get comprehensive voting summary for an event."""
        event = self.get_object()
        
        serializer = EventVotingSummarySerializer(
            event,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[CanVoteOnTimeslot])
    def bulk_vote(self, request, slug=None):
        """Vote for multiple timeslots in an event."""
        event = self.get_object()
        
        serializer = BulkVoteSerializer(
            data=request.data,
            context={
                'request': request,
                'event_slug': slug
            }
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                result = serializer.save()
            
            return Response({
                'message': 'Bulk voting completed',
                'results': result,
                'event': {
                    'slug': event.slug,
                    'title': event.title
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
