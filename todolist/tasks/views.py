from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Count, Q, Max
from datetime import timedelta
from .models import Task, SubTask


# ============================
#  TASK LIST VIEW
# ============================
@login_required
def task_list(request):
    """
    Display all tasks for the current user with filter, sort, and pagination
    """
    tasks = Task.objects.filter(user=request.user)
    
    # Get filter parameters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    deadline_filter = request.GET.get('deadline')  # 'overdue', 'today', 'week', 'month'
    
    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Deadline filters
    if deadline_filter:
        now = timezone.now()
        if deadline_filter == 'overdue':
            # Tasks with deadline in the past and not completed
            tasks = tasks.filter(deadline__lt=now).exclude(status='completed')
        elif deadline_filter == 'today':
            # Tasks due today
            tasks = tasks.filter(
                deadline__date=now.date()
            )
        elif deadline_filter == 'week':
            # Tasks due this week
            week_end = now + timezone.timedelta(days=7)
            tasks = tasks.filter(
                deadline__gte=now,
                deadline__lte=week_end
            )
        elif deadline_filter == 'month':
            # Tasks due this month
            month_end = now + timezone.timedelta(days=30)
            tasks = tasks.filter(
                deadline__gte=now,
                deadline__lte=month_end
            )
    
    # Get sort parameter
    sort_by = request.GET.get('sort', '-created_at')  # Default: newest first
    
    # Validate sort parameter
    valid_sorts = [
        'created_at', '-created_at',  # By creation date
        'deadline', '-deadline',  # By deadline
        'priority', '-priority',  # By priority
        'status', '-status',  # By status
        'title', '-title',  # By title
    ]
    
    if sort_by in valid_sorts:
        # Handle sorting with nulls for deadline
        if sort_by in ['deadline', '-deadline']:
            # Put tasks without deadline at the end
            if sort_by == 'deadline':
                tasks = tasks.order_by('deadline', 'created_at')
            else:
                tasks = tasks.order_by('-deadline', 'created_at')
        else:
            tasks = tasks.order_by(sort_by)
    else:
        tasks = tasks.order_by('-created_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(tasks, 10)  # 10 tasks per page
    
    try:
        tasks_page = paginator.page(page)
    except PageNotAnInteger:
        tasks_page = paginator.page(1)
    except EmptyPage:
        tasks_page = paginator.page(paginator.num_pages)
    
    context = {
        'tasks': tasks_page,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'deadline_filter': deadline_filter,
        'sort_by': sort_by,
        'paginator': paginator,
    }
    return render(request, 'tasks/task_list.html', context)


# ============================
#  TASK DETAIL VIEW
# ============================
@login_required
def task_detail(request, task_id):
    """
    Display task detail with subtasks
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    subtasks = task.subtasks.all()
    
    # Calculate progress
    total_subtasks = subtasks.count()
    completed_subtasks = subtasks.filter(status='completed').count()
    progress_percent = (completed_subtasks / total_subtasks * 100) if total_subtasks > 0 else 0
    
    context = {
        'task': task,
        'subtasks': subtasks,
        'total_subtasks': total_subtasks,
        'completed_subtasks': completed_subtasks,
        'progress_percent': round(progress_percent, 1),
    }
    return render(request, 'tasks/task_detail.html', context)


# ============================
#  TASK CREATE VIEW
# ============================
@login_required
def task_create(request):
    """
    Create a new task
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        priority = request.POST.get('priority', 'medium')
        status = request.POST.get('status', 'pending')
        
        # Validate required fields
        if not title:
            messages.error(request, 'Please enter task title!')
            return redirect('task_create')
        
        # Create task
        task = Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            deadline=deadline if deadline else None,
            priority=priority,
            status=status
        )
        
        messages.success(request, f'Task "{task.title}" created successfully!')
        return redirect('tasks:task_detail', task_id=task.id)
    
    context = {
        'priority_choices': Task.PRIORITY_CHOICES,
        'status_choices': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/task_form.html', context)


# ============================
#  TASK UPDATE VIEW
# ============================
@login_required
def task_update(request, task_id):
    """
    Update an existing task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.deadline = request.POST.get('deadline')
        task.priority = request.POST.get('priority', 'medium')
        task.status = request.POST.get('status', 'pending')
        
        # Validate required fields
        if not task.title:
            messages.error(request, 'Please enter task title!')
            return redirect('tasks:task_update', task_id=task.id)
        
        # Handle empty deadline
        if not task.deadline:
            task.deadline = None
        
        task.save()
        
        messages.success(request, f'Task "{task.title}" updated successfully!')
        return redirect('tasks:task_detail', task_id=task.id)
    
    context = {
        'task': task,
        'priority_choices': Task.PRIORITY_CHOICES,
        'status_choices': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/task_form.html', context)


# ============================
#  TASK DELETE VIEW
# ============================
@login_required
def task_delete(request, task_id):
    """
    Delete a task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('tasks:task_list')
    
    context = {
        'task': task,
    }
    return render(request, 'tasks/task_confirm_delete.html', context)


# ============================
#  DASHBOARD VIEW
# ============================
@login_required
def dashboard(request):
    """
    Main dashboard with task statistics
    """
    user_tasks = Task.objects.filter(user=request.user)
    
    # Calculate statistics
    total_tasks = user_tasks.count()
    pending_tasks = user_tasks.filter(status='pending').count()
    in_progress_tasks = user_tasks.filter(status='in_progress').count()
    completed_tasks = user_tasks.filter(status='completed').count()
    
    # Get overdue tasks
    overdue_tasks = [task for task in user_tasks if task.is_overdue]
    
    # Get recent tasks (last 5)
    recent_tasks = user_tasks[:5]
    
    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'overdue_count': len(overdue_tasks),
        'recent_tasks': recent_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)

#Minh
@login_required
def task_calendar(request):
    return render(request, 'tasks/task_calendar.html')

from django.http import JsonResponse

@login_required
def task_calendar_events(request):
    tasks = Task.objects.filter(
        user=request.user,
        deadline__isnull=False
    )

    events = []

    for task in tasks:
        if task.is_overdue:
            status = 'overdue'
            color = '#dc3545'
        elif task.status == 'completed':
            status = 'completed'
            color = '#198754'
        elif task.status == 'in_progress':
            status = 'in_progress'
            color = '#ffc107'
        else:
            status = 'pending'
            color = '#0d6efd'

        events.append({
            'id': str(task.id),
            'title': task.title,
            'start': task.deadline.isoformat(),
            'url': f'/tasks/{task.id}/',
            'color': color,  
            'extendedProps': {
                'status': status,
                'status_label': status.replace('_', ' ').title(),
                'status_color': color
            }
        })

    return JsonResponse(events, safe=False)


# ============================
#  TODAY VIEW - Sơn (Week 4)
# ============================
@login_required
def today_view(request):
    """
    Display tasks due today
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Get tasks due today
    tasks_today = Task.objects.filter(
        user=request.user,
        deadline__gte=today_start,
        deadline__lt=today_end
    ).order_by('deadline')
    
    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        user=request.user,
        deadline__lt=now,
        status__in=['pending', 'in_progress']
    ).order_by('deadline')
    
    # Get completed today
    completed_today = Task.objects.filter(
        user=request.user,
        completed_at__gte=today_start,
        completed_at__lt=today_end
    ).order_by('-completed_at')
    
    context = {
        'tasks_today': tasks_today,
        'overdue_tasks': overdue_tasks,
        'completed_today': completed_today,
        'today_date': now.date(),
    }
    return render(request, 'tasks/today.html', context)


# ============================
#  WEEKLY VIEW - Sơn (Week 4)
# ============================
@login_required
def weekly_view(request):
    """
    Display tasks for the current week
    """
    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())  # Monday
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    
    # Get tasks for this week
    tasks_this_week = Task.objects.filter(
        user=request.user,
        deadline__gte=week_start,
        deadline__lt=week_end
    ).order_by('deadline')
    
    # Group tasks by day
    days_tasks = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_tasks = tasks_this_week.filter(
            deadline__gte=day,
            deadline__lt=day_end
        )
        days_tasks[day.date()] = list(day_tasks)
    
    context = {
        'week_start': week_start.date(),
        'week_end': week_end.date(),
        'days_tasks': days_tasks,
        'total_tasks': tasks_this_week.count(),
        'completed_tasks': tasks_this_week.filter(status='completed').count(),
    }
    return render(request, 'tasks/weekly_view.html', context)


# ============================
#  MONTHLY VIEW - Sơn (Week 4)
# ============================
@login_required
def monthly_view(request):
    """
    Display tasks for the current month
    """
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate next month start
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)
    
    # Get tasks for this month
    tasks_this_month = Task.objects.filter(
        user=request.user,
        deadline__gte=month_start,
        deadline__lt=month_end
    ).order_by('deadline')
    
    # Group tasks by week
    weeks_tasks = {}
    current_date = month_start
    week_num = 1
    
    while current_date < month_end:
        week_end = current_date + timedelta(days=7)
        week_tasks = tasks_this_month.filter(
            deadline__gte=current_date,
            deadline__lt=week_end
        )
        weeks_tasks[f'Week {week_num}'] = {
            'start': current_date.date(),
            'end': min(week_end, month_end).date(),
            'tasks': list(week_tasks)
        }
        current_date = week_end
        week_num += 1
    
    total_tasks = tasks_this_month.count()
    completed_tasks = tasks_this_month.filter(status='completed').count()
    progress_percentage = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    context = {
        'month_name': month_start.strftime('%B %Y'),
        'month_start': month_start.date(),
        'month_end': month_end.date(),
        'weeks_tasks': weeks_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'tasks/monthly_view.html', context)


# ============================
#  PROGRESS STATISTICS API - Sơn (Week 4)
# ============================
@login_required
def progress_statistics_api(request):
    """
    API endpoint for task progress statistics
    Returns comprehensive statistics about user's tasks
    """
    user_tasks = Task.objects.filter(user=request.user)
    
    # Overall statistics
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(status='completed').count()
    pending_tasks = user_tasks.filter(status='pending').count()
    in_progress_tasks = user_tasks.filter(status='in_progress').count()
    cancelled_tasks = user_tasks.filter(status='cancelled').count()
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Overdue tasks
    now = timezone.now()
    overdue_tasks = user_tasks.filter(
        deadline__lt=now,
        status__in=['pending', 'in_progress']
    ).count()
    
    # Priority breakdown
    priority_stats = {
        'high': user_tasks.filter(priority='high').count(),
        'medium': user_tasks.filter(priority='medium').count(),
        'low': user_tasks.filter(priority='low').count(),
    }
    
    # Time-based statistics
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Tasks created in different periods
    created_this_week = user_tasks.filter(created_at__gte=week_ago).count()
    created_this_month = user_tasks.filter(created_at__gte=month_ago).count()
    
    # Tasks completed in different periods
    completed_this_week = user_tasks.filter(
        completed_at__gte=week_ago,
        completed_at__isnull=False
    ).count()
    completed_this_month = user_tasks.filter(
        completed_at__gte=month_ago,
        completed_at__isnull=False
    ).count()
    
    # Average completion time
    completed_with_time = user_tasks.filter(
        completed_at__isnull=False
    )
    
    avg_completion_days = None
    if completed_with_time.exists():
        total_days = sum([
            (task.completed_at - task.created_at).days 
            for task in completed_with_time
        ])
        avg_completion_days = total_days / completed_with_time.count()
    
    # Upcoming deadlines
    upcoming_7_days = user_tasks.filter(
        deadline__gte=now,
        deadline__lt=now + timedelta(days=7),
        status__in=['pending', 'in_progress']
    ).count()
    
    upcoming_30_days = user_tasks.filter(
        deadline__gte=now,
        deadline__lt=now + timedelta(days=30),
        status__in=['pending', 'in_progress']
    ).count()
    
    statistics = {
        'overview': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'cancelled_tasks': cancelled_tasks,
            'completion_rate': round(completion_rate, 2),
            'overdue_tasks': overdue_tasks,
        },
        'priority_breakdown': priority_stats,
        'activity': {
            'created_this_week': created_this_week,
            'created_this_month': created_this_month,
            'completed_this_week': completed_this_week,
            'completed_this_month': completed_this_month,
            'avg_completion_days': round(avg_completion_days, 1) if avg_completion_days else None,
        },
        'upcoming': {
            'next_7_days': upcoming_7_days,
            'next_30_days': upcoming_30_days,
        }
    }
    
    return JsonResponse(statistics)


# ============================
#  AI ASSISTANT PAGE
# ============================
@login_required
def ai_assistant(request):
    """
    AI Assistant page for users to try AI features
    """
    return render(request, 'tasks/ai_assistant.html')


# ============================
#  SUBTASK VIEWS
# ============================
@login_required
def subtask_create(request, task_id):
    """
    Create a new subtask for a task (AJAX endpoint)
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        import json
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)
        
        # Get max order for this task
        max_order = task.subtasks.aggregate(Max('order'))['order__max'] or 0
        
        subtask = SubTask.objects.create(
            task=task,
            title=title,
            description=description,
            order=max_order + 1
        )
        
        return JsonResponse({
            'success': True,
            'subtask': {
                'id': str(subtask.id),
                'title': subtask.title,
                'description': subtask.description,
                'status': subtask.status,
                'order': subtask.order,
                'created_at': subtask.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_update(request, subtask_id):
    """
    Update a subtask (AJAX endpoint)
    """
    if request.method == 'POST':
        subtask = get_object_or_404(SubTask, id=subtask_id, task__user=request.user)
        
        import json
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'title' in data:
            subtask.title = data['title'].strip()
        if 'description' in data:
            subtask.description = data['description'].strip()
        if 'status' in data:
            subtask.status = data['status']
        if 'order' in data:
            subtask.order = data['order']
        
        subtask.save()
        
        return JsonResponse({
            'success': True,
            'subtask': {
                'id': str(subtask.id),
                'title': subtask.title,
                'description': subtask.description,
                'status': subtask.status,
                'order': subtask.order,
                'is_completed': subtask.is_completed
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_delete(request, subtask_id):
    """
    Delete a subtask (AJAX endpoint)
    """
    if request.method == 'POST':
        subtask = get_object_or_404(SubTask, id=subtask_id, task__user=request.user)
        subtask.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Subtask deleted successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_toggle(request, subtask_id):
    """
    Toggle subtask completion status (AJAX endpoint)
    """
    if request.method == 'POST':
        subtask = get_object_or_404(SubTask, id=subtask_id, task__user=request.user)
        
        # Toggle status
        if subtask.status == 'completed':
            subtask.status = 'pending'
        else:
            subtask.status = 'completed'
        
        subtask.save()
        
        return JsonResponse({
            'success': True,
            'subtask': {
                'id': str(subtask.id),
                'status': subtask.status,
                'is_completed': subtask.is_completed,
                'completed_at': subtask.completed_at.strftime('%Y-%m-%d %H:%M:%S') if subtask.completed_at else None
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_reorder(request, task_id):
    """
    Reorder subtasks for a task (for drag & drop)
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        import json
        data = json.loads(request.body)
        subtask_orders = data.get('orders', [])  # List of {id: ..., order: ...}
        
        # Update orders
        for item in subtask_orders:
            subtask_id = item.get('id')
            new_order = item.get('order')
            
            if subtask_id and new_order is not None:
                SubTask.objects.filter(
                    id=subtask_id,
                    task=task
                ).update(order=new_order)
        
        return JsonResponse({
            'success': True,
            'message': 'Subtasks reordered successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

