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
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            if '@' in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(username=identifier).first()
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

