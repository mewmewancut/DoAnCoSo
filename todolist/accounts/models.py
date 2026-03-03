import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from cloudinary_storage.storage import MediaCloudinaryStorage


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email"),
        help_text=_("Email address used for account activation and password reset"),
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_("Avatar"),
        help_text=_("Profile picture (recommended size: 200x200px)"),
        storage=MediaCloudinaryStorage(),
    )
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def get_full_name_or_username(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    def is_account_activated(self):
        return self.is_active
    
    def get_display_name(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None
