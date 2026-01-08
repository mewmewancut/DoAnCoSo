from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Account activation
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    
    # Password reset
    path("password-reset/", views.ResetPasswordView.as_view(), name="password_reset"),
    path(
        "password-reset-done/",
        views.ResetPasswordDoneView.as_view(),
        name="password_reset_done"
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.ResetPasswordConfirmView.as_view(),
        name="password_reset_confirm"
    ),
    path(
        "password-reset-complete/",
        views.ResetPasswordCompleteView.as_view(),
        name="password_reset_complete"
    ),
    
    # Dashboard
    path("user-dashboard/", views.user_dashboard, name="user_dashboard"),
    
    # Profile
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/change-password/", views.password_change_view, name="password_change"),
    path("profile/delete/", views.account_delete, name="account_delete"),
]
