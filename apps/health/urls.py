from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('ready/', views.ready_check, name='ready_check'),
    path('live/', views.live_check, name='live_check'),
    path('status/', views.status_dashboard, name='status_dashboard'),
]
