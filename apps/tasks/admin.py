from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""
    
    list_display = ('title', 'event', 'status', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'event', 'created_at', 'updated_at')
    search_fields = ('title', 'event__title', 'assigned_to__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = [
        ('Task Information', {
            'fields': ('event', 'title', 'status', 'assigned_to')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    ]
