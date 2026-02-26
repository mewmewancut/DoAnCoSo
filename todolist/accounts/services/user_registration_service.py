import logging
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class UserRegistrationService:
    @staticmethod
    def register_user(form, request=None):
        try:
            user = form.save(commit=False)
            # Activate immediately so user can login right away
            user.is_active = True
            user.save()

            logger.info(f"New user registered: {user.username} ({user.email})")

            return {
                'success': True,
                'user': user,
                'message': _(
                    "Registration successful! "
                    "You can now log in with your account."
                ),
                'error': None,
            }

        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return {
                'success': False,
                'user': None,
                'message': _("An error occurred during registration. Please try again later."),
                'error': str(e),
            }