import logging
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class UserProfileService:
    @staticmethod
    def get_profile_statistics(user):
        try:
            from tasks.models import Task
            
            from django.utils import timezone

            user_tasks = Task.objects.filter(user=user)
            total_tasks = user_tasks.count()
            completed_tasks = user_tasks.filter(status='completed').count()
            pending_tasks = user_tasks.filter(status='pending').count()
            in_progress_tasks = user_tasks.filter(status='in_progress').count()
            overdue_count = user_tasks.filter(
                deadline__lt=timezone.now(),
                status__in=['pending', 'in_progress'],
            ).count()
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'overdue_count': overdue_count
            }
            
        except ImportError:
            logger.warning("Tasks app not available, returning zero statistics")
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'pending_tasks': 0,
                'in_progress_tasks': 0,
                'overdue_count': 0
            }
        
    @staticmethod
    def update_profile(form, user):
        try:
            form.save()
            logger.info(f"Profile updated for user: {user.username} ({user.email})")
            
            return {
                'success': True,
                'message': _("Update profile successfully!"),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user.username}: {str(e)}")
            return {
                'success': False,
                'message': _("An error occurred while updating your profile. Please try again."),
                'error': str(e)
            }

