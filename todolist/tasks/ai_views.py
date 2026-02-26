"""
AI API views for TodoList application.

These endpoints delegate all AI logic to the ``ai_assistant`` app
(LCEL chains + Pydantic validation).  Views only handle HTTP
request/response and persistence of AISuggestion history.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
import json
import logging

from ai_assistant.chains import (
    improve_description,
    suggest_priority,
    generate_subtasks,
)
from .models import AISuggestion, Task

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
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
        
        # Call AI chain (LCEL + Pydantic validated)
        improved = improve_description(title, description)
        
        # Save AI suggestion to history
        AISuggestion.objects.create(
            user=request.user,
            suggestion_type='description',
            input_data={'title': title, 'description': description},
            output_data={'improved_description': improved}
        )
        
        # Return success response
        return JsonResponse({
            'success': True,
            'improved_description': improved,
            'original_title': title,
            'original_description': description
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except Exception as e:
        logger.exception("improve_description_api failed")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
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
        
        # Call AI chain (LCEL + Pydantic validated)
        result = suggest_priority(title, description, deadline)
        
        # Save AI suggestion to history
        AISuggestion.objects.create(
            user=request.user,
            suggestion_type='priority',
            input_data={
                'title': title,
                'description': description,
                'deadline': deadline_str
            },
            output_data={
                'priority': result['priority'],
                'reason': result['reason']
            }
        )
        
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
        logger.exception("suggest_priority_api failed")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def generate_subtasks_api(request):
    """
    API endpoint to generate subtasks from a complex task using AI
    
    POST /api/task/generate-subtasks
    Body: {
        "title": "Task title",
        "description": "Task description (optional)",
        "count": 5 (optional, default 5, range 3-10)
    }
    
    Response: {
        "success": true,
        "subtasks": ["Subtask 1", "Subtask 2", ...],
        "count": 5,
        "original_title": "Task title"
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        count = data.get('count', 5)
        
        # Validate count
        try:
            count = int(count)
            count = max(3, min(10, count))  # Clamp between 3 and 10
        except (ValueError, TypeError):
            count = 5
        
        # Validate input
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)
        
        # Call AI chain (LCEL + Pydantic validated — returns list of dicts with time_estimate)
        subtask_items = generate_subtasks(title, description, count)
        
        # Extract just the titles for backward-compat response
        subtask_titles = [item['title'] for item in subtask_items]
        
        # Save AI suggestion to history (store full items with time estimates)
        AISuggestion.objects.create(
            user=request.user,
            suggestion_type='subtasks',
            input_data={'title': title, 'description': description, 'count': count},
            output_data={'subtasks': subtask_items}
        )
        
        # Return success response
        return JsonResponse({
            'success': True,
            'subtasks': subtask_titles,
            'subtask_details': subtask_items,
            'count': len(subtask_items),
            'original_title': title
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except Exception as e:
        logger.exception("generate_subtasks_api failed")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def ai_history_api(request):
    """
    API endpoint to get recent AI activities for the current user
    
    GET /api/ai-history/
    Query params:
        limit (optional): Number of items to return (default 10, max 50)
    
    Response: {
        "success": true,
        "history": [
            {
                "id": 1,
                "type": "description|priority|subtasks",
                "title": "Task title",
                "created_at": "2 hours ago",
                "input_data": {...},
                "output_data": {...}
            },
            ...
        ],
        "total": 25
    }
    """
    try:
        from django.utils.timesince import timesince
        from django.utils import timezone
        
        # Get limit from query params
        limit = request.GET.get('limit', 10)
        try:
            limit = min(int(limit), 50)  # Max 50 items
        except (ValueError, TypeError):
            limit = 10
        
        # Get recent AI suggestions for this user
        suggestions = AISuggestion.objects.filter(
            user=request.user
        ).order_by('-created_at')[:limit]
        
        # Format history data
        history = []
        for suggestion in suggestions:
            # Get title from input_data
            title = suggestion.input_data.get('title', 'Unknown')
            if len(title) > 50:
                title = title[:50] + '...'
            
            # Format timestamp
            try:
                time_ago = timesince(suggestion.created_at, timezone.now()) + ' ago'
            except:
                time_ago = suggestion.created_at.strftime('%Y-%m-%d %H:%M')
            
            history.append({
                'id': suggestion.id,
                'type': suggestion.suggestion_type,
                'title': title,
                'created_at': time_ago,
                'input_data': suggestion.input_data,
                'output_data': suggestion.output_data
            })
        
        # Get total count
        total = AISuggestion.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'history': history,
            'total': total
        })
        
    except Exception as e:
        logger.exception("ai_history_api failed")
        return JsonResponse({
            'success': False,
            'error': 'Failed to load AI history.'
        }, status=500)