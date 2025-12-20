from django.db import models
from django.contrib.auth.models import User

# Model Activation không được sử dụng (dùng default_token_generator thay vì lưu token)
# class Activation(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     token = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.user.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_unique = models.EmailField(unique=True)