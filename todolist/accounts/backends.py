from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows login with either
    username or email.  Inactive users are allowed through
    ``authenticate()`` so the calling view/service can show the
    correct "account not activated" message instead of the
    misleading "invalid credentials" error.
    """

    def user_can_authenticate(self, user):
        """Always return True so inactive users are returned by
        authenticate().  The view layer will check is_active and
        show the proper message."""
        return True

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')

        if username is None or password is None:
            return None

        # Normalize input
        identifier = username.strip()

        try:
            if '@' in identifier:
                user = User.objects.get(email__iexact=identifier)
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            # Run the password hasher to mitigate timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            if '@' in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(username=identifier).first()

        if user and user.check_password(password):
            return user

        return None

