from typing import Type, Union
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse
from drf_spectacular.openapi import AutoSchema

from .models import Event, TimeSlot
from .permissions import IsEventCreatorOrReadOnly, CanModifyEventContent, CanModifyTimeSlot
from .serializers import (
    EventListSerializer, EventDetailSerializer, EventCreateSerializer,
    EventUpdateSerializer, EventLockSerializer, TimeSlotSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List Events",
        description="""
        Retrieve a paginated list of all events with advanced filtering and search capabilities.
        
        **Features**:
        - Full-text search across event titles and descriptions
        - Filter by status (active, completed, cancelled)
        - Filter by creator
        - Order by creation date, title, or start date
        
        **Permissions**: Available to all users (no authentication required).
        **Rate Limit**: 100 requests per minute per user.
        """,
        tags=["Events"],
        responses={
            200: OpenApiResponse(
                response=EventListSerializer(many=True),
                description='List of events retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Events List',
                        summary='Sample events response',
                        description='Paginated list of events',
                        value={
                            'count': 25,
                            'next': 'http://localhost:8000/api/v1/events/?page=2',
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'title': 'Team Building Workshop',
                                    'description': 'Monthly team building activities',
                                    'created_by': {
                                        'id': 1,
                                        'name': 'John Doe',
                                        'email': 'john@example.com'
                                    },
                                    'status': 'active',
                                    'created_at': '2023-12-01T10:30:00Z',
                                    'timeslots_count': 3,
                                    'total_votes': 15
                                }
                            ]
                        }
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        summary="Create Event",
        description="""
        Create a new community event with timeslots for voting.
        
        **Required Fields**:
        - title: Event name (3-200 characters)
        - description: Event details (optional)
        - timeslots: Array of available time options
        
        **Authentication Required**: Bearer token in Authorization header.
        **Rate Limit**: 20 requests per minute per user.
        """,
        tags=["Events"],
        examples=[
            OpenApiExample(
                'Create Event',
                summary='Create a new event',
                description='Example event creation request',
                value={
                    'title': 'Monthly Team Meeting',
                    'description': 'Discussion of quarterly goals and updates',
                    'timeslots': [
                        {
                            'start_time': '2024-01-15T14:00:00Z',
                            'end_time': '2024-01-15T15:30:00Z',
                            'description': 'Monday afternoon option'
                        },
                        {
                            'start_time': '2024-01-16T10:00:00Z',
                            'end_time': '2024-01-16T11:30:00Z',
                            'description': 'Tuesday morning option'
                        }
                    ]
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=EventDetailSerializer,
                description='Event created successfully',
                examples=[
                    OpenApiExample(
                        'Event Created',
                        summary='Successful event creation',
                        description='New event with generated ID',
                        value={
                            'id': 1,
                            'title': 'Monthly Team Meeting',
                            'description': 'Discussion of quarterly goals and updates',
                            'created_by': {
                                'id': 1,
                                'name': 'John Doe',
                                'email': 'john@example.com'
                            },
                            'status': 'active',
                            'is_locked': False,
                            'created_at': '2023-12-01T10:30:00Z',
                            'timeslots': [
                                {
                                    'id': 1,
                                    'start_time': '2024-01-15T14:00:00Z',
                                    'end_time': '2024-01-15T15:30:00Z',
                                    'description': 'Monday afternoon option',
                                    'vote_count': 0
                                },
                                {
                                    'id': 2,
                                    'start_time': '2024-01-16T10:00:00Z',
                                    'end_time': '2024-01-16T11:30:00Z',
                                    'description': 'Tuesday morning option',
                                    'vote_count': 0
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid event data',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        summary='Invalid event fields',
                        description='Event validation failed',
                        value={
                            'title': ['This field is required.'],
                            'timeslots': ['At least one timeslot is required.']
                        }
                    )
                ]
            )
        }
    ),
    retrieve=extend_schema(
        summary="Get Event Details",
        description="""
        Retrieve detailed information about a specific event including all timeslots and voting data.
        
        **Includes**:
        - Complete event information
        - All associated timeslots
        - Vote counts for each timeslot
        - Creator information
        
        **Permissions**: Available to all users.
        """,
        tags=["Events"],
        responses={
            200: OpenApiResponse(
                response=EventDetailSerializer,
                description='Event details retrieved successfully'
            ),
            404: OpenApiResponse(
                description='Event not found',
                examples=[
                    OpenApiExample(
                        'Event Not Found',
                        summary='Invalid event ID',
                        description='Event does not exist',
                        value={
                            'detail': 'Not found.'
                        }
                    )
                ]
            )
        }
    ),
    update=extend_schema(
        summary="Update Event",
        description="""
        Update an existing event completely.
        
        **Permissions**: Only the event creator can update their events.
        **Restrictions**: Cannot update locked events.
        **Authentication Required**: Bearer token in Authorization header.
        """,
        tags=["Events"],
        responses={
            200: OpenApiResponse(
                response=EventDetailSerializer,
                description='Event updated successfully'
            ),
            403: OpenApiResponse(
                description='Permission denied or event locked',
                examples=[
                    OpenApiExample(
                        'Event Locked',
                        summary='Cannot modify locked event',
                        description='Event is locked for modifications',
                        value={
                            'detail': 'Event is locked and cannot be modified.'
                        }
                    )
                ]
            )
        }
    ),
    partial_update=extend_schema(
        summary="Partially Update Event",
        description="""
        Update specific fields of an existing event.
        
        Only provided fields will be updated. Supports partial modifications.
        
        **Permissions**: Only the event creator can update their events.
        **Restrictions**: Cannot update locked events.
        **Authentication Required**: Bearer token in Authorization header.
        """,
        tags=["Events"]
    ),
    destroy=extend_schema(
        summary="Delete Event",
        description="""
        Permanently delete an event and all associated data.
        
        **Warning**: This action cannot be undone. All timeslots and votes will be deleted.
        
        **Permissions**: Only the event creator can delete their events.
        **Authentication Required**: Bearer token in Authorization header.
        """,
        tags=["Events"],
        responses={
            204: OpenApiResponse(description='Event deleted successfully'),
            403: OpenApiResponse(
                description='Permission denied',
                examples=[
                    OpenApiExample(
                        'Not Owner',
                        summary='User is not event creator',
                        description='Only event creators can delete events',
                        value={
                            'detail': 'You do not have permission to perform this action.'
                        }
                    )
                ]
            )
        }
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing events with full CRUD operations.
    
    - List: All users can view events
    - Create: Authenticated users only
    - Retrieve: All users can view event details
    - Update/Delete: Only event creator
    - Lock: Only event creator (custom action)
    """
    
    queryset = Event.objects.select_related('created_by').prefetch_related(
        'time_slots__votes__user'
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsEventCreatorOrReadOnly, CanModifyEventContent]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self) -> Type[BaseSerializer]:  # type: ignore[override]
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'create':
            return EventCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EventUpdateSerializer
        elif self.action == 'lock':
            return EventLockSerializer
        else:
            return EventDetailSerializer
    
    def perform_create(self, serializer):
        """Set the creator to the current user."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        summary="Lock event",
        description="Lock an event to prevent further modifications. Only the creator can lock their events.",
        request=EventLockSerializer,
        responses={200: EventDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEventCreatorOrReadOnly])
    def lock(self, request, slug=None):
        """Lock an event to prevent further modifications."""
        event = self.get_object()
        
        serializer = EventLockSerializer(
            data=request.data,
            context={'event': event, 'request': request}
        )
        
        if serializer.is_valid():
            event = serializer.save()
            response_serializer = EventDetailSerializer(event, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="List event timeslots",
        description="Get all timeslots for a specific event."
    ),
    create=extend_schema(
        summary="Create timeslot",
        description="Add a new timeslot to an event. Only possible for draft events."
    ),
    retrieve=extend_schema(
        summary="Get timeslot details",
        description="Get details of a specific timeslot."
    ),
    update=extend_schema(
        summary="Update timeslot",
        description="Update a timeslot. Only possible for draft events."
    ),
    partial_update=extend_schema(
        summary="Partially update timeslot",
        description="Partially update a timeslot. Only possible for draft events."
    ),
    destroy=extend_schema(
        summary="Delete timeslot",
        description="Delete a timeslot. Only possible for draft events."
    ),
)
class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timeslots within events.
    
    Timeslots are nested under events and can only be modified when the parent event is in draft status.
    """
    
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated, IsEventCreatorOrReadOnly, CanModifyTimeSlot]
    
    def get_queryset(self) -> QuerySet[TimeSlot]:  # type: ignore[override]
        """Filter timeslots by event slug with vote optimization."""
        event_slug = self.kwargs.get('event_slug')
        if event_slug:
            return TimeSlot.objects.filter(
                event__slug=event_slug
            ).select_related('event').prefetch_related('votes__user')
        return TimeSlot.objects.none()
    
    def get_event(self):
        """Get the parent event."""
        event_slug = self.kwargs.get('event_slug')
        return get_object_or_404(Event, slug=event_slug)
    
    def perform_create(self, serializer):
        """Set the event to the parent event."""
        event = self.get_event()
        
        # Check if event is locked
        if event.status == 'locked':
            raise serializers.ValidationError("Cannot add timeslots to locked events.")
        
        # Check if user is the creator
        if event.created_by != self.request.user:
            raise serializers.ValidationError("Only the event creator can add timeslots.")
            
        serializer.save(event=event)
    
    def check_object_permissions(self, request, obj):
        """Check permissions for the parent event."""
        # First check if user can modify the event
        if obj.event.created_by != request.user:
            self.permission_denied(request, message="Only the event creator can modify timeslots.")
        
        # Then check the default permissions
        super().check_object_permissions(request, obj)
