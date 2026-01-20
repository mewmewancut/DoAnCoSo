"""
URL configuration for tasks app
"""

from django.urls import path
from . import views
from . import ai_views
app_name = "tasks" 


urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Task CRUD
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<uuid:task_id>/', views.task_detail, name='task_detail'),
    path('<uuid:task_id>/edit/', views.task_update, name='task_update'),
    path('<uuid:task_id>/delete/', views.task_delete, name='task_delete'),
   
    # Minh - Calendar
    path('calendar/', views.task_calendar, name='task_calendar'),
    path('calendar/events/', views.task_calendar_events, name='task_calendar_events'),
    
    # Sơn - Week 4: Time-based views
    path('today/', views.today_view, name='today'),
    path('weekly/', views.weekly_view, name='weekly'),
    path('monthly/', views.monthly_view, name='monthly'),
    path('api/statistics/', views.progress_statistics_api, name='progress_statistics'),
    
    # AI Assistant Page
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
  
    # SubTask CRUD endpoints
    path('<uuid:task_id>/subtasks/create/', views.subtask_create, name='subtask_create'),
    path('subtasks/<uuid:subtask_id>/update/', views.subtask_update, name='subtask_update'),
    path('subtasks/<uuid:subtask_id>/delete/', views.subtask_delete, name='subtask_delete'),
    path('subtasks/<uuid:subtask_id>/toggle/', views.subtask_toggle, name='subtask_toggle'),
    path('<uuid:task_id>/subtasks/reorder/', views.subtask_reorder, name='subtask_reorder'),
    
    # Dũng - AI API endpoints
    path('api/improve-description/', ai_views.improve_description_api, name='ai_improve_description'),
    path('api/suggest-priority/', ai_views.suggest_priority_api, name='ai_suggest_priority'),
    path('api/generate-subtasks/', ai_views.generate_subtasks_api, name='ai_generate_subtasks'),
]
