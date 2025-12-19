from django.urls import path
from .views import *
from . import views
urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),

    # Forgot password
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    path("password-reset-done/", ResetPasswordDoneView.as_view(), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/",ResetPasswordConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset-complete/",ResetPasswordCompleteView.as_view(), name="password_reset_complete"),
    
    path("logout/", logout_view, name="logout"),
    path("user-dashboard/", user_dashboard, name="user_dashboard"),
]
