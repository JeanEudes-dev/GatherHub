from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VoteViewSet, TimeslotVotingViewSet, EventVotingViewSet

app_name = 'voting'

# Create router for API endpoints
router = DefaultRouter()
router.register(r'votes', VoteViewSet, basename='vote')
router.register(r'timeslots', TimeslotVotingViewSet, basename='timeslot-voting')
router.register(r'events', EventVotingViewSet, basename='event-voting')

urlpatterns = [
    path('', include(router.urls)),
]
