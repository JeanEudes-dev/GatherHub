"""
WebSocket URL routing for GatherHub.
"""

from django.urls import re_path
from .consumers.event import EventConsumer
from .consumers.voting import VotingConsumer
from .consumers.tasks import TasksConsumer

websocket_urlpatterns = [
    # General event updates
    re_path(r'ws/events/(?P<event_slug>[\w-]+)/$', EventConsumer.as_asgi()),
    
    # Voting-specific updates
    re_path(r'ws/events/(?P<event_slug>[\w-]+)/voting/$', VotingConsumer.as_asgi()),
    
    # Task-specific updates
    re_path(r'ws/events/(?P<event_slug>[\w-]+)/tasks/$', TasksConsumer.as_asgi()),
]
