from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

app_name = 'tasks'

# Create router for task endpoints
router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
