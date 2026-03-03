import logging
from django.utils.translation import gettext as _
from django.conf import settings
from ..utils import send_activation_email

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class UserRegistrationService:
    @staticmethod
    def register_user(form, request=None):
        try:
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            logger.info(f"New user registered: {user.username} ({user.email})")

            email_sent = send_activation_email(user, request)

            if email_sent:
                return {
                    'success': True,
                    'user': user,
                    'message': _(
                        "Registration successful! "
                        "Please check your email to activate your account."
                    ),
                    'error': None
                }

            logger.error(
                f"Activation email failed to send for user: {user.username} ({user.email})"
            )
            return {
                'success': True,
                'user': user,
                'message': _(
                    "Registration successful, but we could not send the activation email. "
                    "Please try again later or contact support to activate your account."
                ),
                'error': 'email_send_failed',
            }
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return {
                'success': False,
                'user': None,
                'message': _("An error occurred during registration. Please try again later."),
                'error': str(e),
            }