import logging
from django.contrib.auth import get_user_model

from ..utils import send_activation_email

logger = logging.getLogger(__name__)

class UserRegistrationService:   
    @staticmethod
    def register_user(form, request=None):
        try:
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            logger.info(f"New user registered: {user.username} ({user.email})")
            
            # Send activation email
            email_sent = send_activation_email(user, request)
            
            if email_sent:
                return {
                    'success': True,
                    'user': user,
                    'message': "Registration successful! Please check your email to activate your account.",
                    'error': None
                }
            else:
                logger.error(f"Failed to send activation email for user: {user.email}")
                return {
                    'success': True,  
                    'user': user,
                    'message': "Registration successful but failed to send activation email. Please contact the administrator.",
                    'error': 'email_send_failed'
                }
                
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return {
                'success': False,
                'user': None,
                'message': "An error occurred during registration. Please try again later.",
                'error': str(e)
            }

