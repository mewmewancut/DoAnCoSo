"""
AI API views for TodoList application
These endpoints provide AI-powered features for task management
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from ai_utils import improve_task_description


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
