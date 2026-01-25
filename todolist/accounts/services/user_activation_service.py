import logging
from django.contrib.auth.tokens import default_token_generator

from ..utils import get_user_from_uidb64

logger = logging.getLogger(__name__)

class UserActivationService:    
    @staticmethod
    def activate_user(uidb64, token):
        user = get_user_from_uidb64(uidb64)
        
        if user is None:
            logger.warning(f"Invalid activation attempt with uidb64: {uidb64}")
            return {
                'success': False,
                'user': None,
                'message': "Activation link is invalid or has expired.",
                'error': 'invalid_uidb64',
                'already_activated': False
            }
        
        # Check if already activated
        if user.is_active:
            return {
                'success': True,
                'user': user,
                'message': "Your account is already activated!",
                'error': None,
                'already_activated': True
            }
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            logger.warning(f"Invalid activation token for user: {user.email}")
            return {
                'success': False,
                'user': user,
                'message': "Activation link is invalid or has expired.",
                'error': 'invalid_token',
                'already_activated': False
            }
        
        # Activate user
        try:
            user.is_active = True
            user.save(update_fields=['is_active'])
            logger.info(f"User activated successfully: {user.username} ({user.email})")
            
            return {
                'success': True,
                'user': user,
                'message': "Account activated successfully! Please log in.",
                'error': None,
                'already_activated': False
            }
            
        except Exception as e:
            logger.error(f"Error activating user {user.email}: {str(e)}")
            return {
                'success': False,
                'user': user,
                'message': "An error occurred while activating your account. Please try again.",
                'error': str(e),
                'already_activated': False
            }

