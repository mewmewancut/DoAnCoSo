import logging
from django.contrib.auth import update_session_auth_hash

logger = logging.getLogger(__name__)

class UserAccountService:    
    @staticmethod
    def change_password(form, request):
        try:
            form.save()
            update_session_auth_hash(request, form.user)
            logger.info(f"Password changed for user: {request.user.username}")
            
            return {
                'success': True,
                'message': "Change password successfully!",
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error changing password for user {request.user.username}: {str(e)}")
            return {
                'success': False,
                'message': "An error occurred while changing your password. Please try again.",
                'error': str(e)
            }
    
    @staticmethod
    def validate_username_confirmation(user, confirm_username):
        if confirm_username.strip() != user.username:
            return {
                'valid': False,
                'message': "Username does not match. Please enter the correct username to confirm."
            }
        
        return {
            'valid': True,
            'message': None
        }
    
    @staticmethod
    def delete_user_account(user):
        try:
            username = user.username
            email = user.email            
            try:
                from tasks.models import Task
                Task.objects.filter(user=user).delete()
                logger.info(f"Deleted all tasks for user: {username}")
            except ImportError:
                pass            
            user.delete()
            
            logger.warning(f"User account deleted: {username} ({email})")
            
            return {
                'success': True,
                'username': username,
                'email': email,
                'message': "Your account has been deleted successfully.",
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error deleting user account {user.username}: {str(e)}")
            return {
                'success': False,
                'username': user.username if hasattr(user, 'username') else 'Unknown',
                'email': user.email if hasattr(user, 'email') else 'Unknown',
                'message': "An error occurred while deleting your account. Please try again.",
                'error': str(e)
            }

