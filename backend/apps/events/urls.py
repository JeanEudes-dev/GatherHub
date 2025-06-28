from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventViewSet, TimeSlotViewSet
from apps.tasks.views import EventTaskViewSet

app_name = 'events'

# Create main router for events
router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    # Manually add timeslot endpoints since nested routing is complex
    path('<slug:event_slug>/timeslots/', TimeSlotViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='timeslot-list'),
    path('<slug:event_slug>/timeslots/<int:pk>/', TimeSlotViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='timeslot-detail'),
    # Add task endpoints
    path('<slug:event_slug>/tasks/', EventTaskViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='task-list'),
]
