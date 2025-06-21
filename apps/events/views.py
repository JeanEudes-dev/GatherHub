from typing import Type, Union
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Event, TimeSlot
from .permissions import IsEventCreatorOrReadOnly, CanModifyEventContent, CanModifyTimeSlot
from .serializers import (
    EventListSerializer, EventDetailSerializer, EventCreateSerializer,
    EventUpdateSerializer, EventLockSerializer, TimeSlotSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List events",
        description="Get a paginated list of all events with filtering and search capabilities."
    ),
    create=extend_schema(
        summary="Create event",
        description="Create a new event. Authenticated users only."
    ),
    retrieve=extend_schema(
        summary="Get event details",
        description="Get detailed information about a specific event including all timeslots."
    ),
    update=extend_schema(
        summary="Update event",
        description="Update an event. Only the creator can update their events and only if not locked."
    ),
    partial_update=extend_schema(
        summary="Partially update event",
        description="Partially update an event. Only the creator can update their events and only if not locked."
    ),
    destroy=extend_schema(
        summary="Delete event",
        description="Delete an event. Only the creator can delete their events."
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
