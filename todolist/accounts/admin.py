from django.contrib import admin

# Register your models here.

#Minh
from django.contrib.auth.admin import UserAdmin
from .models import User  

admin.site.register(User, UserAdmin)