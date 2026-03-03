from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
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
        if user and user.check_password(password):
            return user

        return None

