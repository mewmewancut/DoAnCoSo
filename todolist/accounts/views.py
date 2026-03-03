import logging
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext as _
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegisterForm, ProfileEditForm, CustomPasswordChangeForm
from .services import (
    UserRegistrationService,
    UserActivationService,
    UserAuthenticationService,
    UserProfileService,
    UserAccountService,
)

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
@never_cache
def register(request):
    if request.user.is_authenticated:
        messages.info(request, _("You are already logged in."))
        return redirect("tasks:dashboard")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            result = UserRegistrationService.register_user(form, request)
            
            if result['success']:
                if result['error'] == 'email_send_failed':
                    messages.warning(request, result['message'])
                else:
                    messages.success(request, result['message'])
                return redirect("accounts:login")
            messages.error(request, result['message'])
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})



@never_cache
def activate(request, uidb64, token):
    result = UserActivationService.activate_user(uidb64, token)
    
    if result['success']:
        if result['already_activated']:
            messages.info(request, result['message'])
        else:
            messages.success(request, result['message'])
        return redirect("accounts:login")
    else:
        messages.error(request, result['message'])
        return redirect("accounts:register")



@require_http_methods(["GET", "POST"])
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect("tasks:dashboard")
    
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.GET.get("next") or request.POST.get("next")

        result = UserAuthenticationService.authenticate_user(request, identifier, password)
        
        if result['success']:
            if next_url and url_has_allowed_host_and_scheme(next_url,allowed_hosts={request.get_host()}):
                return redirect(next_url)
            messages.success(request, result['message'])
            return redirect("tasks:dashboard")
        else:
            messages.error(request, result['message'])

    return render(request, "accounts/login.html", {"next": request.GET.get("next")})

@login_required
@never_cache
def logout_view(request):
    result = UserAuthenticationService.logout_user(request)
    messages.success(request, result['message'])
    return redirect("accounts:login")

@login_required
def profile_view(request):
    user = request.user
    stats = UserProfileService.get_profile_statistics(user)
    
    context = {
        "user": user,
        **stats
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
    user = request.user
    
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user, user=user)
        if form.is_valid():
            result = UserProfileService.update_profile(form, user)
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect("accounts:profile")
            else:
                messages.error(request, result['message'])
    else:
        form = ProfileEditForm(instance=user, user=user)
    
    return render(request, "accounts/profile_edit.html", {"form": form, "user": user})


@login_required
def password_change_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            result = UserAccountService.change_password(form, request)
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect("accounts:profile")
            else:
                messages.error(request, result['message'])
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, "accounts/password_change.html", {"form": form})

@login_required
def account_delete(request):
    user = request.user
    
    if request.method == "POST":
        confirm_username = request.POST.get('confirm_username', '').strip()
        
        # Validate username confirmation
        validation = UserAccountService.validate_username_confirmation(user, confirm_username)
        if not validation['valid']:
            messages.error(request, validation['message'])
            return render(request, "accounts/account_delete.html", {"user": user})
        
        # Delete account
        result = UserAccountService.delete_user_account(user)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect("home")
        else:
            messages.error(request, result['message'])
    
    return render(request, "accounts/account_delete.html", {"user": user})



@never_cache
def password_reset_view(request, *args, **kwargs):
    class _ResetPasswordView(auth_views.PasswordResetView):
        template_name = "accounts/password_reset.html"
        email_template_name = "accounts/password_reset_email.txt"
        html_email_template_name = "accounts/password_reset_email.html"
        subject_template_name = "accounts/password_reset_subject.txt"
        success_url = reverse_lazy("accounts:password_reset_done")

        def form_valid(self, form):
            email = form.cleaned_data["email"]
            logger.info(f"Password reset requested for email: {email}")
            return super().form_valid(form)

    return _ResetPasswordView.as_view()(request, *args, **kwargs)


@never_cache
def password_reset_done_view(request, *args, **kwargs):
    return auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html",
    )(request, *args, **kwargs)


@never_cache
def password_reset_confirm_view(request, uidb64, token, *args, **kwargs):
    class _ResetPasswordConfirmView(auth_views.PasswordResetConfirmView):
        template_name = "accounts/password_reset_confirm.html"
        success_url = reverse_lazy("accounts:password_reset_complete")

        def form_valid(self, form):
            user = form.user
            logger.info(f"Password reset successful for user: {user.username} ({user.email})")
            return super().form_valid(form)

    return _ResetPasswordConfirmView.as_view()(
        request,
        uidb64=uidb64,
        token=token,
        *args,
        **kwargs,
    )


@never_cache
def password_reset_complete_view(request, *args, **kwargs):
    return auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html",
    )(request, *args, **kwargs)