from django.contrib import admin
from .models import Task, AISuggestion, SubTask, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'deadline', 'created_at', 'completed_at']
    list_filter = ['status', 'priority', 'tags', 'created_at', 'deadline']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'description', 'tags')
        }),
        ('Task Details', {
            'fields': ('priority', 'status', 'deadline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = ['suggestion_type', 'user', 'task', 'applied', 'created_at']
    list_filter = ['suggestion_type', 'applied', 'created_at']
    search_fields = ['user__email', 'task__title']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'task', 'suggestion_type', 'applied')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'status', 'order', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'task__title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'task', 'title', 'description')
        }),
        ('Status & Order', {
            'fields': ('status', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
