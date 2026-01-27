"""
Calendar Service - Business logic for calendar views and events
"""
from django.utils import timezone
from datetime import timedelta
from ..models import Task


class CalendarService:
    """
    Service class for calendar-related functionality
    """
    
    @staticmethod
    def get_calendar_events(user):
        """
        Get all tasks with deadlines formatted for FullCalendar
        
        Returns:
            List of event dictionaries for FullCalendar
        """
        tasks = Task.objects.filter(
            user=user,
            deadline__isnull=False
        )
        
        events = []
        for task in tasks:
            event = CalendarService._task_to_event(task)
            events.append(event)
        
        return events
    
    @staticmethod
    def _task_to_event(task):
        """
        Convert a task to FullCalendar event format
        
        Args:
            task: Task instance
        
        Returns:
            Dict formatted for FullCalendar
        """
        # Determine status and color
        if task.is_overdue:
            status = 'overdue'
            color = '#dc3545'  # Red
        elif task.status == 'completed':
            status = 'completed'
            color = '#198754'  # Green
        elif task.status == 'in_progress':
            status = 'in_progress'
            color = '#ffc107'  # Yellow
        else:
            status = 'pending'
            color = '#0d6efd'  # Blue
        
        return {
            'id': str(task.id),
            'title': task.title,
            'start': timezone.localtime(task.deadline).isoformat(),
            'url': f'/tasks/{task.id}/',
            'color': color,
            'extendedProps': {
                'status': status,
                'status_label': status.replace('_', ' ').title(),
                'status_color': color,
                'priority': task.priority,
                'description': task.description or '',
            }
        }
    
    @staticmethod
    def get_today_data(user):
        """
        Get task data for today view
        
        Returns:
            Dict with today's tasks, overdue tasks, and completed today
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Tasks due today
        tasks_today = Task.objects.filter(
            user=user,
            deadline__gte=today_start,
            deadline__lt=today_end
        ).order_by('deadline')
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            user=user,
            deadline__lt=now,
            status__in=['pending', 'in_progress']
        ).order_by('deadline')
        
        # Completed today
        completed_today = Task.objects.filter(
            user=user,
            completed_at__gte=today_start,
            completed_at__lt=today_end
        ).order_by('-completed_at')
        
        return {
            'tasks_today': tasks_today,
            'overdue_tasks': overdue_tasks,
            'completed_today': completed_today,
            'today_date': now.date(),
        }
    
    @staticmethod
    def get_weekly_data(user):
        """
        Get task data for weekly view
        
        Returns:
            Dict with week info and tasks grouped by day
        """
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())  # Monday
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        # Get tasks for this week
        tasks_this_week = Task.objects.filter(
            user=user,
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
        
        return {
            'week_start': week_start.date(),
            'week_end': week_end.date(),
            'days_tasks': days_tasks,
            'total_tasks': tasks_this_week.count(),
            'completed_tasks': tasks_this_week.filter(status='completed').count(),
        }
    
    @staticmethod
    def get_monthly_data(user):
        """
        Get task data for monthly view
        
        Returns:
            Dict with month info and tasks grouped by week
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
            user=user,
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
        
        return {
            'month_name': month_start.strftime('%B %Y'),
            'month_start': month_start.date(),
            'month_end': month_end.date(),
            'weeks_tasks': weeks_tasks,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_percentage': progress_percentage,
        }
