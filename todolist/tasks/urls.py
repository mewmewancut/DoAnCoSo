"""
URL configuration for tasks app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Task CRUD
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<uuid:task_id>/', views.task_detail, name='task_detail'),
    path('<uuid:task_id>/edit/', views.task_update, name='task_update'),
    path('<uuid:task_id>/delete/', views.task_delete, name='task_delete'),
]
