"""
AI API views for TodoList application
These endpoints provide AI-powered features for task management
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json

from ai_utils import improve_task_description, suggest_task_priority, generate_task_subtasks


@login_required
@require_http_methods(["POST"])
@csrf_exempt  # TODO: Add proper CSRF handling for production
def improve_description_api(request):
    """
    API endpoint to improve task description using AI
    
    POST /api/task/improve-description
    Body: {
        "title": "Task title",
        "description": "Current description (optional)"
    }
    
    Response: {
        "success": true,
        "improved_description": "AI-improved description",
        "original_title": "Task title",
        "original_description": "Current description"
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        # Validate input
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)
        
        # Call AI function
        improved_description = improve_task_description(title, description)
        
        # Return success response
        return JsonResponse({
            'success': True,
            'improved_description': improved_description,
            'original_title': title,
            'original_description': description
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt  # TODO: Add proper CSRF handling for production
def suggest_priority_api(request):
    """
    API endpoint to suggest task priority using AI
    
    POST /api/task/suggest-priority
    Body: {
        "title": "Task title",
        "description": "Task description (optional)",
        "deadline": "2026-01-15T10:00:00" (optional, ISO format)
    }
    
    Response: {
        "success": true,
        "priority": "HIGH|MEDIUM|LOW",
        "reason": "Explanation for the suggestion",
        "original_title": "Task title"
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        deadline_str = data.get('deadline', '').strip()
        
        # Validate input
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)
        
        # Parse deadline
        deadline = None
        if deadline_str:
            try:
                deadline = parse_datetime(deadline_str)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }, status=400)
        
        # Call AI function
        result = suggest_task_priority(title, description, deadline)
        
        # Return success response
        return JsonResponse({
            'success': True,
            'priority': result['priority'],
            'reason': result['reason'],
            'original_title': title
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
