"""
Task Service - Business logic for Task CRUD operations
"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
from ..models import Task


class TaskService:
    """
    Service class for Task business logic
    Separates business logic from views
    """
    
    # Valid sort options
    VALID_SORTS = [
        'created_at', '-created_at',  # By creation date
        'deadline', '-deadline',       # By deadline
        'priority', '-priority',       # By priority
        'status', '-status',           # By status
        'title', '-title',             # By title
    ]
    
    @staticmethod
    def get_user_tasks(user):
        """Get all tasks for a specific user"""
        return Task.objects.filter(user=user)
    
    @staticmethod
    def get_task_by_id(task_id, user):
        """Get a specific task by ID ensuring it belongs to the user"""
        return Task.objects.filter(id=task_id, user=user).first()
    
    @classmethod
    def get_filtered_tasks(cls, user, status=None, priority=None, deadline_filter=None):
        """
        Get tasks with optional filters
        
        Args:
            user: The user to filter tasks for
            status: Filter by status ('pending', 'in_progress', 'completed', 'cancelled')
            priority: Filter by priority ('low', 'medium', 'high')
            deadline_filter: Filter by deadline ('overdue', 'today', 'week', 'month')
        
        Returns:
            QuerySet of filtered tasks
        """
        tasks = cls.get_user_tasks(user)
        
        # Apply status filter
        if status:
            tasks = tasks.filter(status=status)
        
        # Apply priority filter
        if priority:
            tasks = tasks.filter(priority=priority)
        
        # Apply deadline filter
        if deadline_filter:
            tasks = cls._apply_deadline_filter(tasks, deadline_filter)
        
        return tasks
    
    @staticmethod
    def _apply_deadline_filter(tasks, deadline_filter):
        """Apply deadline-based filtering"""
        now = timezone.now()
        
        if deadline_filter == 'overdue':
            # Tasks with deadline in the past and not completed
            return tasks.filter(deadline__lt=now).exclude(status='completed')
        
        elif deadline_filter == 'today':
            # Tasks due today
            return tasks.filter(deadline__date=now.date())
        
        elif deadline_filter == 'week':
            # Tasks due this week
            week_end = now + timedelta(days=7)
            return tasks.filter(deadline__gte=now, deadline__lte=week_end)
        
        elif deadline_filter == 'month':
            # Tasks due this month
            month_end = now + timedelta(days=30)
            return tasks.filter(deadline__gte=now, deadline__lte=month_end)
        
        return tasks
    
    @classmethod
    def get_sorted_tasks(cls, tasks, sort_by='-created_at'):
        """
        Sort tasks by given field
        
        Args:
            tasks: QuerySet of tasks
            sort_by: Sort field (prefix with '-' for descending)
        
        Returns:
            Sorted QuerySet
        """
        if sort_by not in cls.VALID_SORTS:
            sort_by = '-created_at'
        
        # Handle sorting with nulls for deadline
        if sort_by in ['deadline', '-deadline']:
            # Put tasks without deadline at the end
            if sort_by == 'deadline':
                return tasks.order_by('deadline', 'created_at')
            else:
                return tasks.order_by('-deadline', 'created_at')
        
        return tasks.order_by(sort_by)
    
    @staticmethod
    def paginate_tasks(tasks, page=1, per_page=10):
        """
        Paginate tasks
        
        Args:
            tasks: QuerySet of tasks
            page: Page number (1-indexed)
            per_page: Number of items per page
        
        Returns:
            Tuple of (paginated_tasks, paginator)
        """
        paginator = Paginator(tasks, per_page)
        
        try:
            paginated = paginator.page(page)
        except PageNotAnInteger:
            paginated = paginator.page(1)
        except EmptyPage:
            paginated = paginator.page(paginator.num_pages)
        
        return paginated, paginator
    
    @staticmethod
    def create_task(user, title, description=None, deadline=None, 
                   priority='medium', status='pending'):
        """
        Create a new task
        
        Args:
            user: The user creating the task
            title: Task title (required)
            description: Task description
            deadline: Task deadline (datetime or None)
            priority: Task priority ('low', 'medium', 'high')
            status: Initial status
        
        Returns:
            Created Task instance
        """
        return Task.objects.create(
            user=user,
            title=title,
            description=description,
            deadline=deadline if deadline else None,
            priority=priority,
            status=status
        )
    
    @staticmethod
    def update_task(task, title, description=None, deadline=None, 
                   priority='medium', status='pending'):
        """
        Update an existing task
        
        Args:
            task: Task instance to update
            title: New title
            description: New description
            deadline: New deadline
            priority: New priority
            status: New status
        
        Returns:
            Updated Task instance
        """
        task.title = title
        task.description = description
        task.deadline = deadline if deadline else None
        task.priority = priority
        task.status = status
        task.save()
        return task
    
    @staticmethod
    def update_task_status(task, new_status):
        """
        Quick update for task status only
        
        Args:
            task: Task instance
            new_status: New status value
        
        Returns:
            Updated Task instance
        """
        task.status = new_status
        task.save()
        return task
    
    @staticmethod
    def delete_task(task):
        """Delete a task"""
        task.delete()
    
    @staticmethod
    def get_overdue_tasks(user):
        """Get all overdue tasks for a user"""
        now = timezone.now()
        return Task.objects.filter(
            user=user,
            deadline__lt=now,
            status__in=['pending', 'in_progress']
        ).order_by('deadline')
    
    @staticmethod
    def get_tasks_for_date(user, target_date):
        """Get tasks due on a specific date"""
        return Task.objects.filter(
            user=user,
            deadline__date=target_date
        ).order_by('deadline')
    
    @staticmethod
    def get_tasks_for_date_range(user, start_date, end_date):
        """Get tasks within a date range"""
        return Task.objects.filter(
            user=user,
            deadline__gte=start_date,
            deadline__lt=end_date
        ).order_by('deadline')
    
    @staticmethod
    def get_completed_tasks_for_date_range(user, start_date, end_date):
        """Get tasks completed within a date range"""
        return Task.objects.filter(
            user=user,
            completed_at__gte=start_date,
            completed_at__lt=end_date
        ).order_by('-completed_at')
    
    @staticmethod
    def get_recent_tasks(user, limit=5):
        """Get the most recent tasks for a user"""
        return Task.objects.filter(user=user)[:limit]
    
    @staticmethod
    def calculate_task_progress(task):
        """
        Calculate subtask completion progress for a task
        
        Returns:
            Dict with total, completed, and percentage
        """
        subtasks = task.subtasks.all()
        total = subtasks.count()
        completed = subtasks.filter(status='completed').count()
        percentage = (completed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'completed': completed,
            'percentage': round(percentage, 1)
        }
