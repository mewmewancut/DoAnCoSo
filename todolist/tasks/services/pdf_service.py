"""
PDF Service - Business logic for PDF generation and download previews
"""
from django.utils import timezone
from datetime import date, timedelta
import calendar
from ..models import Task


class PDFService:
    """
    Service class for PDF generation functionality
    """
    
    @staticmethod
    def get_week_tasks(user):
        """
        Get tasks for the current week (for PDF export)
        
        Returns:
            Dict with tasks and date range
        """
        today = timezone.now().date()
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)  # Sunday
        
        tasks = Task.objects.filter(
            user=user,
            deadline__date__range=(start, end)
        ).order_by('deadline')
        
        return {
            'tasks': tasks,
            'start': start,
            'end': end,
        }
    
    @staticmethod
    def get_month_tasks(user):
        """
        Get tasks for the current month (for PDF export)
        
        Returns:
            Dict with tasks and date range
        """
        today = timezone.now().date()
        year = today.year
        month = today.month
        
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])
        
        tasks = Task.objects.filter(
            user=user,
            deadline__date__range=(start, end)
        ).order_by('deadline')
        
        return {
            'tasks': tasks,
            'start': start,
            'end': end,
        }
    
    @staticmethod
    def get_pdf_data(user, pdf_type='week'):
        """
        Get data for PDF generation based on type
        
        Args:
            user: User instance
            pdf_type: 'week' or 'month'
        
        Returns:
            Dict with tasks, date range, template, and filename
        """
        today = timezone.now().date()
        
        if pdf_type == 'month':
            year, month = today.year, today.month
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            template = 'tasks/pdf/month.html'
            filename = f'tasks_month_{month}_{year}.pdf'
        else:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            template = 'tasks/pdf/week.html'
            filename = f'tasks_week_{start}_{end}.pdf'
        
        tasks = Task.objects.filter(
            user=user,
            deadline__range=(start, end)
        ).order_by('deadline')
        
        return {
            'tasks': tasks,
            'start': start,
            'end': end,
            'template': template,
            'filename': filename,
        }
    
    @staticmethod
    def get_custom_range_tasks(user, start_date, end_date):
        """
        Get tasks for a custom date range
        
        Args:
            user: User instance
            start_date: Start date
            end_date: End date
        
        Returns:
            Dict with tasks and date range
        """
        tasks = Task.objects.filter(
            user=user,
            deadline__date__range=(start_date, end_date)
        ).order_by('deadline')
        
        return {
            'tasks': tasks,
            'start': start_date,
            'end': end_date,
        }
    
    @staticmethod
    def get_task_summary_for_pdf(tasks):
        """
        Generate summary statistics for PDF export
        
        Args:
            tasks: QuerySet of tasks
        
        Returns:
            Dict with summary statistics
        """
        total = tasks.count()
        completed = tasks.filter(status='completed').count()
        pending = tasks.filter(status='pending').count()
        in_progress = tasks.filter(status='in_progress').count()
        
        high_priority = tasks.filter(priority='high').count()
        medium_priority = tasks.filter(priority='medium').count()
        low_priority = tasks.filter(priority='low').count()
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'completion_rate': round((completed / total * 100), 1) if total > 0 else 0,
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
        }
