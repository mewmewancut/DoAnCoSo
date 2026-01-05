from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'deadline']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'description')
        }),
        ('Task Details', {
            'fields': ('priority', 'status', 'deadline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
