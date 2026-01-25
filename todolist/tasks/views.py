"""
Views for Tasks app - TodoList application
Refactored to use service layer for business logic
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
import json

# PDF generation
from xhtml2pdf import pisa

# Models
from .models import Task, SubTask

# Services
from .services import (
    TaskService,
    SubtaskService,
    StatisticsService,
    CalendarService,
    PDFService,
)


# ============================
#  TASK LIST VIEW
# ============================
@login_required
def task_list(request):
    """
    Display all tasks for the current user with filter, sort, and pagination
    """
    # Get filter parameters
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    deadline_filter = request.GET.get("deadline")
    sort_by = request.GET.get("sort", "-created_at")
    page = request.GET.get("page", 1)

    # Use services for business logic
    tasks = TaskService.get_filtered_tasks(
        user=request.user, status=status_filter, priority=priority_filter, deadline_filter=deadline_filter
    )

    tasks = TaskService.get_sorted_tasks(tasks, sort_by)
    tasks_page, paginator = TaskService.paginate_tasks(tasks, page)

    context = {
        "tasks": tasks_page,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "deadline_filter": deadline_filter,
        "sort_by": sort_by,
        "paginator": paginator,
    }
    return render(request, "tasks/task_list.html", context)


# ============================
#  TASK DETAIL VIEW
# ============================
@login_required
def task_detail(request, task_id):
    """
    Display task detail with subtasks
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    subtasks = SubtaskService.get_subtasks_for_task(task)
    progress = TaskService.calculate_task_progress(task)

    context = {
        "task": task,
        "subtasks": subtasks,
        "total_subtasks": progress["total"],
        "completed_subtasks": progress["completed"],
        "progress_percent": progress["percentage"],
    }
    return render(request, "tasks/task_detail.html", context)


# ============================
#  TASK CREATE VIEW
# ============================
@login_required
def task_create(request):
    """
    Create a new task
    """
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")
        priority = request.POST.get("priority", "medium")
        status = request.POST.get("status", "pending")

        # Validate required fields
        if not title:
            messages.error(request, "Please enter task title!")
            return redirect("tasks:task_create")

        # Create task using service
        task = TaskService.create_task(
            user=request.user, title=title, description=description, deadline=deadline, priority=priority, status=status
        )

        messages.success(request, f'Task "{task.title}" created successfully!')
        return redirect("tasks:task_detail", task_id=task.id)

    context = {"priority_choices": Task.PRIORITY_CHOICES, "status_choices": Task.STATUS_CHOICES}
    return render(request, "tasks/task_form.html", context)


# ============================
#  TASK UPDATE VIEW
# ============================
@login_required
def task_update(request, task_id):
    """
    Update an existing task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")
        priority = request.POST.get("priority", "medium")
        status = request.POST.get("status", "pending")

        # Validate required fields
        if not title:
            messages.error(request, "Please enter task title!")
            return redirect("tasks:task_update", task_id=task.id)

        # Update task using service
        TaskService.update_task(
            task=task, title=title, description=description, deadline=deadline, priority=priority, status=status
        )

        messages.success(request, f'Task "{task.title}" updated successfully!')
        return redirect("tasks:task_detail", task_id=task.id)

    context = {"task": task, "priority_choices": Task.PRIORITY_CHOICES, "status_choices": Task.STATUS_CHOICES}
    return render(request, "tasks/task_form.html", context)


# ============================
#  TASK DELETE VIEW
# ============================
@login_required
def task_delete(request, task_id):
    """
    Delete a task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        task_title = task.title
        TaskService.delete_task(task)
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect("tasks:task_list")

    context = {"task": task}
    return render(request, "tasks/task_confirm_delete.html", context)


# ============================
#  TASK QUICK STATUS UPDATE (API)
# ============================
@login_required
def task_quick_status(request, task_id):
    """
    Quick update task status via AJAX
    """
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id, user=request.user)

        data = json.loads(request.body)
        new_status = data.get("status")

        if new_status not in ["pending", "in_progress", "completed", "cancelled"]:
            return JsonResponse({"success": False, "error": "Invalid status value"}, status=400)

        TaskService.update_task_status(task, new_status)

        return JsonResponse({
            "success": True,
            "task": {"id": str(task.id), "status": task.status, "status_display": task.get_status_display()},
        })

    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


# ============================
#  DASHBOARD VIEW
# ============================
@login_required
def dashboard(request):
    """
    Main dashboard with task statistics
    """
    data = StatisticsService.get_dashboard_data(request.user)
    return render(request, "tasks/dashboard.html", data)


# ============================
#  CALENDAR VIEWS
# ============================
@login_required
def task_calendar(request):
    """Calendar view page"""
    return render(request, "tasks/task_calendar.html")


@login_required
def task_calendar_events(request):
    """API endpoint for calendar events (FullCalendar)"""
    events = CalendarService.get_calendar_events(request.user)
    return JsonResponse(events, safe=False)


# ============================
#  TODAY VIEW
# ============================
@login_required
def today_view(request):
    """
    Display tasks due today
    """
    data = CalendarService.get_today_data(request.user)
    return render(request, "tasks/today.html", data)


# ============================
#  WEEKLY VIEW
# ============================
@login_required
def weekly_view(request):
    """
    Display tasks for the current week
    """
    data = CalendarService.get_weekly_data(request.user)
    return render(request, "tasks/weekly_view.html", data)


# ============================
#  MONTHLY VIEW
# ============================
@login_required
def monthly_view(request):
    """
    Display tasks for the current month
    """
    data = CalendarService.get_monthly_data(request.user)
    return render(request, "tasks/monthly_view.html", data)


# ============================
#  PROGRESS STATISTICS API
# ============================
@login_required
def progress_statistics_api(request):
    """
    API endpoint for task progress statistics
    Returns comprehensive statistics about user's tasks
    """
    statistics = StatisticsService.get_full_statistics(request.user)
    return JsonResponse(statistics)


# ============================
#  AI ASSISTANT PAGE
# ============================
@login_required
def ai_assistant(request):
    """
    AI Assistant page for users to try AI features
    """
    return render(request, "tasks/ai_assistant.html")


# ============================
#  SUBTASK VIEWS
# ============================
@login_required
def subtask_create(request, task_id):
    """
    Create a new subtask for a task (AJAX endpoint)
    """
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id, user=request.user)

        data = json.loads(request.body)
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)
        
        subtask = SubtaskService.create_subtask(task, title, description)
        
        return JsonResponse({
            'success': True,
            'subtask': SubtaskService.subtask_to_dict(subtask)
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_update(request, subtask_id):
    """
    Update a subtask (AJAX endpoint)
    """
    if request.method == 'POST':
        subtask = SubtaskService.get_subtask_by_id(subtask_id, request.user)
        
        if not subtask:
            return JsonResponse({
                'success': False,
                'error': 'Subtask not found'
            }, status=404)
        
        data = json.loads(request.body)
        
        SubtaskService.update_subtask(
            subtask,
            title=data.get('title'),
            description=data.get('description'),
            status=data.get('status'),
            order=data.get('order')
        )
        
        return JsonResponse({
            'success': True,
            'subtask': SubtaskService.subtask_to_dict(subtask)
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_delete(request, subtask_id):
    """
    Delete a subtask (AJAX endpoint)
    """
    if request.method == 'POST':
        subtask = SubtaskService.get_subtask_by_id(subtask_id, request.user)
        
        if not subtask:
            return JsonResponse({
                'success': False,
                'error': 'Subtask not found'
            }, status=404)
        
        SubtaskService.delete_subtask(subtask)
        
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
        subtask = SubtaskService.get_subtask_by_id(subtask_id, request.user)
        
        if not subtask:
            return JsonResponse({
                'success': False,
                'error': 'Subtask not found'
            }, status=404)
        
        SubtaskService.toggle_subtask(subtask)
        
        return JsonResponse({
            'success': True,
            'subtask': SubtaskService.subtask_to_dict(subtask)
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def subtask_reorder(request, task_id):
    """
    Reorder subtasks for a task (for drag & drop)
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        data = json.loads(request.body)
        subtask_orders = data.get('orders', [])
        
        SubtaskService.reorder_subtasks(task, subtask_orders)
        
        return JsonResponse({
            'success': True,
            'message': 'Subtasks reordered successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


# ============================
#  PDF DOWNLOAD VIEWS
# ============================
@login_required
def download_week_preview(request):
    """Preview page for weekly PDF download"""
    data = PDFService.get_week_tasks(request.user)
    return render(request, 'tasks/download/preview_week.html', data)


@login_required
def download_month_preview(request):
    """Preview page for monthly PDF download"""
    data = PDFService.get_month_tasks(request.user)
    return render(request, 'tasks/download/preview_month.html', data)


@login_required
def download_pdf(request):
    """Generate and download PDF"""
    pdf_type = request.GET.get('type', 'week')
    data = PDFService.get_pdf_data(request.user, pdf_type)
    
    # Render HTML
    html = render_to_string(data['template'], {
        'tasks': data['tasks'],
        'start': data['start'],
        'end': data['end'],
        'user': request.user
    })
    
    # Generate PDF
    result = BytesIO()
    pisa.CreatePDF(html, dest=result)
    
    # Return as download
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{data["filename"]}"'
    return response
