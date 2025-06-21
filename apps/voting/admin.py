from django.contrib import admin
from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface for Vote model."""
    
    list_display = ('user', 'timeslot', 'created_at')
    list_filter = ('timeslot__event', 'created_at')
    search_fields = ('user__email', 'timeslot__event__title')
    readonly_fields = ('created_at',)
    
    fieldsets = [
        ('Vote Information', {
            'fields': ('user', 'timeslot')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    ]
