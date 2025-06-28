from django.contrib import admin
from .models import Event, TimeSlot


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model."""
    
    list_display = ('title', 'status', 'created_by', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'created_by__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = [
        ('Event Information', {
            'fields': ('title', 'slug', 'description', 'status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    ]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """Admin interface for TimeSlot model."""
    
    list_display = ('event', 'datetime', 'created_at')
    list_filter = ('event', 'datetime', 'created_at')
    search_fields = ('event__title',)
    readonly_fields = ('created_at',)
    
    fieldsets = [
        ('Time Slot Information', {
            'fields': ('event', 'datetime')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    ]
