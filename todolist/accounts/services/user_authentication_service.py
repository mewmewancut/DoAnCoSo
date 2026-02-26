import logging
from django.contrib.auth import authenticate, login, logout

logger = logging.getLogger(__name__)


class UserAuthenticationService:
    @staticmethod
    def authenticate_user(request, identifier, password):
        if not identifier or not password:
            return {
                'success': False,
                'user': None,
                'message': "Please enter both email/username and password.",
                'error': 'missing_credentials',
                'inactive': False
            }

        # Authenticate user (backend returns inactive users too so we
        # can show the correct error message)
        user = authenticate(
            request,
            username=identifier,
            password=password,
        )

        if not user:
            logger.warning(f"Failed login attempt for: {identifier}")
            return {
                'success': False,
                'user': None,
                'message': "Invalid email/username or password.",
                'error': 'invalid_credentials',
                'inactive': False
            }

        # Check if account is active — now reachable because the
        # custom backend no longer filters out inactive users.
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {identifier}")
            return {
                'success': False,
                'user': user,
                'message': (
                    "Your account has not been activated yet. "
                    "Please check your email for the activation link, "
                    "or contact the administrator."
                ),
                'error': 'inactive_account',
                'inactive': True
            }

        # Login successful
        login(request, user, backend='accounts.backends.EmailOrUsernameBackend')
        logger.info(f"User logged in: {user.username} ({user.email})")

        return {
            'success': True,
            'user': user,
            'message': "Login successful",
            'error': None,
            'inactive': False
        }
    
    @staticmethod
    def logout_user(request):
        user = request.user
        username = user.username if hasattr(user, 'username') else 'Unknown'
        
        logout(request)
        logger.info(f"User logged out: {username}")
        
        return {
            'success': True,
            'username': username,
            'message': "You have been logged out successfully!"
        }

