"""
Statistics Service - Business logic for task statistics and progress
"""
from django.utils import timezone
from datetime import timedelta
from ..models import Task


class StatisticsService:
    """
    Service class for generating task statistics
    """
    
    @staticmethod
    def get_overview_stats(user):
        """
        Get overall task statistics for a user
        
        Returns:
            Dict with count statistics
        """
        tasks = Task.objects.filter(user=user)
        total = tasks.count()
        completed = tasks.filter(status='completed').count()
        pending = tasks.filter(status='pending').count()
        in_progress = tasks.filter(status='in_progress').count()
        cancelled = tasks.filter(status='cancelled').count()
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'in_progress_tasks': in_progress,
            'cancelled_tasks': cancelled,
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0,
        }
    
    @staticmethod
    def get_overdue_stats(user):
        """
        Get overdue task statistics
        
        Returns:
            Dict with overdue count and list
        """
        now = timezone.now()
        overdue_tasks = Task.objects.filter(
            user=user,
            deadline__lt=now,
            status__in=['pending', 'in_progress']
        ).order_by('deadline')
        
        return {
            'count': overdue_tasks.count(),
            'tasks': list(overdue_tasks)
        }
    
    @staticmethod
    def get_priority_stats(user):
        """
        Get task count by priority
        
        Returns:
            Dict with counts for each priority level
        """
        tasks = Task.objects.filter(user=user)
        return {
            'high': tasks.filter(priority='high').count(),
            'medium': tasks.filter(priority='medium').count(),
            'low': tasks.filter(priority='low').count(),
        }
    
    @staticmethod
    def get_activity_stats(user):
        """
        Get activity statistics (created/completed tasks over time)
        
        Returns:
            Dict with activity metrics
        """
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        tasks = Task.objects.filter(user=user)
        
        # Created tasks
        created_this_week = tasks.filter(created_at__gte=week_ago).count()
        created_this_month = tasks.filter(created_at__gte=month_ago).count()
        
        # Completed tasks
        completed_this_week = tasks.filter(
            completed_at__gte=week_ago,
            completed_at__isnull=False
        ).count()
        completed_this_month = tasks.filter(
            completed_at__gte=month_ago,
            completed_at__isnull=False
        ).count()
        
        return {
            'created_this_week': created_this_week,
            'created_this_month': created_this_month,
            'completed_this_week': completed_this_week,
            'completed_this_month': completed_this_month,
        }
    
    @staticmethod
    def get_average_completion_time(user):
        """
        Calculate average time to complete tasks
        
        Returns:
            Average completion time in days (float) or None
        """
        completed_tasks = Task.objects.filter(
            user=user,
            completed_at__isnull=False
        )
        
        if not completed_tasks.exists():
            return None
        
        total_days = sum([
            (task.completed_at - task.created_at).days 
            for task in completed_tasks
        ])
        
        return round(total_days / completed_tasks.count(), 1)
    
    @staticmethod
    def get_upcoming_deadlines(user):
        """
        Get counts of upcoming deadlines
        
        Returns:
            Dict with counts for different time periods
        """
        now = timezone.now()
        
        tasks = Task.objects.filter(
            user=user,
            status__in=['pending', 'in_progress']
        )
        
        return {
            'next_7_days': tasks.filter(
                deadline__gte=now,
                deadline__lt=now + timedelta(days=7)
            ).count(),
            'next_30_days': tasks.filter(
                deadline__gte=now,
                deadline__lt=now + timedelta(days=30)
            ).count(),
        }
    
    @classmethod
    def get_full_statistics(cls, user):
        """
        Get comprehensive statistics for API response
        
        Returns:
            Dict with all statistics
        """
        overview = cls.get_overview_stats(user)
        overdue = cls.get_overdue_stats(user)
        
        return {
            'overview': {
                **overview,
                'overdue_tasks': overdue['count'],
            },
            'priority_breakdown': cls.get_priority_stats(user),
            'activity': {
                **cls.get_activity_stats(user),
                'avg_completion_days': cls.get_average_completion_time(user),
            },
            'upcoming': cls.get_upcoming_deadlines(user),
        }
    
    @staticmethod
    def get_dashboard_data(user):
        """
        Get data specifically for the dashboard view
        
        Returns:
            Dict with dashboard statistics and lists
        """
        tasks = Task.objects.filter(user=user)
        
        # Basic counts
        total = tasks.count()
        pending = tasks.filter(status='pending').count()
        in_progress = tasks.filter(status='in_progress').count()
        completed = tasks.filter(status='completed').count()
        
        # Overdue tasks
        overdue = [task for task in tasks if task.is_overdue]
        
        # Recent tasks (last 5)
        recent = tasks[:5]
        
        return {
            'total_tasks': total,
            'pending_tasks': pending,
            'in_progress_tasks': in_progress,
            'completed_tasks': completed,
            'overdue_tasks': overdue,
            'overdue_count': len(overdue),
            'recent_tasks': recent,
        }
