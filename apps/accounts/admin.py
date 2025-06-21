from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    
    list_display = ('email', 'name', 'username', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('email', 'name', 'username')
    ordering = ('-date_joined',)
    
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Additional Info', {
            'fields': ('name', 'avatar')
        }),
    ]
    
    add_fieldsets = list(UserAdmin.add_fieldsets) + [
        ('Additional Info', {
            'fields': ('email', 'name', 'avatar')
        }),
    ]
