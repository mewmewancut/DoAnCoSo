from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Task


# ============================
#  TASK LIST VIEW
# ============================
@login_required
def task_list(request):
    """
    Display all tasks for the current user
    """
    tasks = Task.objects.filter(user=request.user)
    
    # Get filter parameters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'tasks/task_list.html', context)


# ============================
#  TASK DETAIL VIEW
# ============================
@login_required
def task_detail(request, task_id):
    """
    Display task detail
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    context = {
        'task': task,
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
            messages.error(request, 'Vui lòng nhập tiêu đề task!')
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
        
        messages.success(request, f'Tạo task "{task.title}" thành công!')
        return redirect('task_detail', task_id=task.id)
    
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
            messages.error(request, 'Vui lòng nhập tiêu đề task!')
            return redirect('task_update', task_id=task.id)
        
        # Handle empty deadline
        if not task.deadline:
            task.deadline = None
        
        task.save()
        
        messages.success(request, f'Cập nhật task "{task.title}" thành công!')
        return redirect('task_detail', task_id=task.id)
    
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
        messages.success(request, f'Đã xóa task "{task_title}"!')
        return redirect('task_list')
    
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
