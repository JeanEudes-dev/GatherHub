from typing import Any, Type
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse
from drf_spectacular.openapi import AutoSchema

from apps.events.models import Event, TimeSlot
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
        summary="List User's Votes",
        description="""
        Retrieve all votes made by the current authenticated user across all events.
        
        **Features**:
        - Filter by event ID
        - Filter by timeslot ID
        - Order by creation date
        
        **Authentication Required**: Bearer token in Authorization header.
        **Rate Limit**: 100 requests per minute per user.
        """,
        tags=["Voting"],
        responses={
            200: OpenApiResponse(
                response=VoteSerializer(many=True),
                description='User votes retrieved successfully',
                examples=[
                    OpenApiExample(
                        'User Votes',
                        summary='List of user votes',
                        description='All votes made by the current user',
                        value={
                            'count': 5,
                            'next': None,
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'timeslot': {
                                        'id': 1,
                                        'start_time': '2024-01-15T14:00:00Z',
                                        'end_time': '2024-01-15T16:00:00Z',
                                        'description': 'Monday afternoon session'
                                    },
                                    'event': {
                                        'id': 1,
                                        'title': 'Team Building Workshop'
                                    },
                                    'created_at': '2023-12-01T10:30:00Z'
                                }
                            ]
                        }
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        summary="Create Vote",
        description="""
        Vote for a specific timeslot in an event.
        
        **Restrictions**:
        - Users can only vote once per timeslot
        - Must be a member of the event to vote
        - Event must allow voting (not locked)
        
        **Authentication Required**: Bearer token in Authorization header.
        **Rate Limit**: 10 requests per minute per user.
        """,
        tags=["Voting"],
        examples=[
            OpenApiExample(
                'Create Vote',
                summary='Vote for a timeslot',
                description='Vote for a specific timeslot',
                value={
                    'timeslot': 1
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=VoteSerializer,
                description='Vote created successfully',
                examples=[
                    OpenApiExample(
                        'Vote Created',
                        summary='Successful vote creation',
                        description='Vote registered for timeslot',
                        value={
                            'id': 1,
                            'timeslot': {
                                'id': 1,
                                'start_time': '2024-01-15T14:00:00Z',
                                'end_time': '2024-01-15T16:00:00Z',
                                'description': 'Monday afternoon session'
                            },
                            'event': {
                                'id': 1,
                                'title': 'Team Building Workshop'
                            },
                            'created_at': '2023-12-01T10:30:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid vote data or duplicate vote',
                examples=[
                    OpenApiExample(
                        'Duplicate Vote',
                        summary='User already voted for this timeslot',
                        description='Attempt to vote twice on same timeslot',
                        value={
                            'non_field_errors': ['You have already voted for this timeslot.']
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description='Permission denied - not event member',
                examples=[
                    OpenApiExample(
                        'Not Event Member',
                        summary='User not allowed to vote',
                        description='User is not a member of the event',
                        value={
                            'detail': 'You must be a member of this event to vote.'
                        }
                    )
                ]
            )
        }
    ),
    destroy=extend_schema(
        summary="Remove Vote",
        description="""
        Remove an existing vote for a timeslot.
        
        **Restrictions**:
        - Users can only remove their own votes
        - Vote must exist and belong to the user
        
        **Authentication Required**: Bearer token in Authorization header.
        **Rate Limit**: 10 requests per minute per user.
        """,
        tags=["Voting"],
        responses={
            204: OpenApiResponse(description='Vote removed successfully'),
            403: OpenApiResponse(
                description='Permission denied - not vote owner',
                examples=[
                    OpenApiExample(
                        'Not Vote Owner',
                        summary='Cannot remove others votes',
                        description='User trying to remove someone elses vote',
                        value={
                            'detail': 'You can only remove your own votes.'
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Vote not found',
                examples=[
                    OpenApiExample(
                        'Vote Not Found',
                        summary='Invalid vote ID',
                        description='Vote does not exist',
                        value={
                            'detail': 'Not found.'
                        }
                    )
                ]
            )
        }
    ),
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
