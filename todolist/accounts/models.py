import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with UUID primary key and email field
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email"),
        help_text=_("Email address used for account activation and password reset"),
    )
    
    # Minh
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
    
    def __str__(self):
        """
        String representation of user
        """
        return f"{self.username} ({self.email})"
    
    def get_full_name_or_username(self):
        """
        Return full name if available, otherwise username
        """
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    def is_account_activated(self):
        """
        Check if account is activated
        """
        return self.is_active
    
    def get_display_name(self):
        """
        Get display name for user (full name > username)
        """
        full_name = self.get_full_name()
        return full_name if full_name else self.username
