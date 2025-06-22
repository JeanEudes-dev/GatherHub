from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Task
from .permissions import (
    IsEventMember, IsTaskAssigneeOrEventCreator, CanModifyTask,
    IsEventCreatorForTaskCreation, CanAssignTasks
)
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer,
    TaskEventCreateSerializer
)
from apps.events.models import Event


@extend_schema_view(
    list=extend_schema(
        summary="List tasks",
        description="Get a paginated list of tasks with filtering capabilities. Users can only see tasks for events they are associated with.",
        parameters=[
            OpenApiParameter(
                name='event',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter tasks by event ID'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter tasks by status (todo, doing, done)'
            ),
            OpenApiParameter(
                name='assigned_to',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter tasks by assigned user ID'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search tasks by title'
            ),
        ]
    ),
    create=extend_schema(
        summary="Create task",
        description="Create a new task. Only event members can create tasks."
    ),
    retrieve=extend_schema(
        summary="Get task details",
        description="Get detailed information about a specific task. Only event members can view."
    ),
    update=extend_schema(
        summary="Update task",
        description="Update a task. Only the event creator or assigned user can update tasks."
    ),
    partial_update=extend_schema(
        summary="Partially update task",
        description="Partially update a task. Only the event creator or assigned user can update tasks."
    ),
    destroy=extend_schema(
        summary="Delete task",
        description="Delete a task. Only the event creator can delete tasks."
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks with full CRUD operations.
    
    - List: Event members can view tasks for their events
    - Create: Event members can create tasks
    - Retrieve: Event members can view task details
    - Update: Event creator or assigned user can update tasks
    - Delete: Only event creator can delete tasks
    """
    
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'status', 'assigned_to']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['status', '-created_at']
    
    def get_queryset(self): # type: ignore
        """
        Filter tasks to only show those for events the user is associated with.
        Event association means: user is event creator or has voted on the event.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        
        # Get events where user is creator
        created_events = Event.objects.filter(created_by=user)
        
        # Get events where user has voted
        voted_events = Event.objects.filter(
            timeslots__votes__user=user
        ).distinct()
        
        # Combine both querysets
        accessible_events = created_events.union(voted_events)
        
        # Return tasks for accessible events
        return Task.objects.filter(
            event__in=accessible_events
        ).select_related('event', 'assigned_to')
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsEventCreatorForTaskCreation]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsEventMember, IsTaskAssigneeOrEventCreator, CanAssignTasks, CanModifyTask]
        else:
            permission_classes = [IsAuthenticated, IsEventMember]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self): # type: ignore
        """Return the appropriate serializer class for the action."""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Set additional fields when creating a task."""
        # No additional logic needed here as event and assigned_to are handled by serializer
        serializer.save()
        
        # Future: Add signal for real-time updates
        # task_created.send(sender=Task, task=serializer.instance, user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="List event tasks",
        description="Get all tasks for a specific event. Only event members can view.",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter tasks by status (todo, doing, done)'
            ),
            OpenApiParameter(
                name='assigned_to',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter tasks by assigned user ID'
            ),
        ]
    ),
    create=extend_schema(
        summary="Create event task",
        description="Create a new task for a specific event. Only event members can create tasks."
    ),
)
class EventTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks within a specific event context.
    
    Provides task management endpoints nested under events:
    - /api/v1/events/{slug}/tasks/
    """
    
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_to']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['status', '-created_at']
    
    def get_event(self):
        """Get the event from the URL slug."""
        event_slug = self.kwargs['event_slug']
        return get_object_or_404(Event, slug=event_slug)
    
    def get_queryset(self): # type: ignore
        """Return tasks for the specific event."""
        event = self.get_event()
        return Task.objects.filter(event=event).select_related('event', 'assigned_to')
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsEventCreatorForTaskCreation]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsEventMember, IsTaskAssigneeOrEventCreator, CanAssignTasks, CanModifyTask]
        else:
            permission_classes = [IsAuthenticated, IsEventMember]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self): # type: ignore
        """Return the appropriate serializer class for the action."""
        if self.action == 'create':
            return TaskEventCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def get_serializer_context(self):
        """Add event to serializer context."""
        context = super().get_serializer_context()
        context['event'] = self.get_event()
        return context
    
    def perform_create(self, serializer):
        """Set the event when creating a task."""
        event = self.get_event()
        serializer.save(event=event)
        
        # Future: Add signal for real-time updates
        # task_created.send(sender=Task, task=serializer.instance, user=self.request.user, event=event)
    
    # Override HTTP methods to only allow list and create for this viewset
    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/v1/tasks/{id}/ for individual task operations."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/v1/tasks/{id}/ for individual task operations."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/v1/tasks/{id}/ for individual task operations."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/v1/tasks/{id}/ for individual task operations."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
