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
  
    
    # Dũng - AI API endpoints
    path('api/improve-description/', ai_views.improve_description_api, name='ai_improve_description'),


]
