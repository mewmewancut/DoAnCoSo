import logging
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth.tokens import default_token_generator

from .forms import RegisterForm
from .utils import send_activation_email, get_user_from_uidb64

logger = logging.getLogger(__name__)
User = get_user_model()

# ============================
#  ĐĂNG KÝ + GỬI MAIL KÍCH HOẠT
# ============================
@require_http_methods(["GET", "POST"])
@never_cache
def register(request):
    """
    User registration view with email activation
    """
    if request.user.is_authenticated:
        messages.info(request, "Bạn đã đăng nhập rồi!")
        return redirect("accounts:user_dashboard")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                
                logger.info(f"New user registered: {user.username} ({user.email})")
                
                # Send activation email
                if send_activation_email(user, request):
                    messages.success(
                        request,
                        "Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản.",
                    )
                else:
                    messages.warning(
                        request,
                        "Đăng ký thành công nhưng không thể gửi email kích hoạt. "
                        "Vui lòng liên hệ quản trị viên.",
                    )
                    logger.error(f"Failed to send activation email for user: {user.email}")
                
                return redirect("accounts:login")
            except Exception as e:
                logger.error(f"Error during user registration: {str(e)}")
                messages.error(
                    request,
                    "Có lỗi xảy ra trong quá trình đăng ký. Vui lòng thử lại sau.",
                )
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# ============================
#  KÍCH HOẠT TÀI KHOẢN
# ============================
@never_cache
def activate(request, uidb64, token):
    """
    Activate user account using token
    """
    user = get_user_from_uidb64(uidb64)
    
    if user is None:
        logger.warning(f"Invalid activation attempt with uidb64: {uidb64}")
        messages.error(request, "Link kích hoạt không hợp lệ hoặc đã hết hạn.")
        return redirect("accounts:register")
    
    if user.is_active:
        messages.info(request, "Tài khoản của bạn đã được kích hoạt rồi!")
        return redirect("accounts:login")
    
    if default_token_generator.check_token(user, token):
        try:
            user.is_active = True
            user.save(update_fields=['is_active'])
            logger.info(f"User activated successfully: {user.username} ({user.email})")
            messages.success(request, "Kích hoạt tài khoản thành công! Hãy đăng nhập.")
            return redirect("accounts:login")
        except Exception as e:
            logger.error(f"Error activating user {user.email}: {str(e)}")
            messages.error(request, "Có lỗi xảy ra khi kích hoạt tài khoản. Vui lòng thử lại.")
            return redirect("accounts:register")
    else:
        logger.warning(f"Invalid activation token for user: {user.email}")
        messages.error(request, "Link kích hoạt không hợp lệ hoặc đã hết hạn.")
        return redirect("accounts:register")


# ============================
#  ĐĂNG NHẬP (EMAIL / USERNAME)
# ============================
@require_http_methods(["GET", "POST"])
@never_cache
def login_view(request):
    """
    User login view with redirect to next parameter support
    """
    if request.user.is_authenticated:
        return redirect("accounts:user_dashboard")
    
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.GET.get("next") or request.POST.get("next")

        if not identifier or not password:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin đăng nhập.")
            return render(request, "accounts/login.html", {"next": next_url})

        user = authenticate(
            request,
            username=identifier,
            password=password,
        )

        if user:
            if user.is_active:
                login(request, user)
                logger.info(f"User logged in: {user.username} ({user.email})")
                
                # Redirect to next URL if provided, otherwise to dashboard
                redirect_url = next_url if next_url else "accounts:user_dashboard"
                return redirect(redirect_url)
            else:
                messages.error(
                    request,
                    "Tài khoản chưa được kích hoạt! Vui lòng kiểm tra email để kích hoạt tài khoản.",
                )
                logger.warning(f"Login attempt for inactive user: {identifier}")
        else:
            messages.error(request, "Sai email/username hoặc mật khẩu")
            logger.warning(f"Failed login attempt for: {identifier}")

    return render(request, "accounts/login.html", {"next": request.GET.get("next")})


# ============================
#  QUÊN MẬT KHẨU (CHUẨN DJANGO)
# ============================
class ResetPasswordView(auth_views.PasswordResetView):
    """
    Password reset view
    """
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    
    def form_valid(self, form):
        """
        Log password reset request
        """
        email = form.cleaned_data['email']
        logger.info(f"Password reset requested for email: {email}")
        return super().form_valid(form)


class ResetPasswordDoneView(auth_views.PasswordResetDoneView):
    """
    Password reset done view
    """
    template_name = "accounts/password_reset_done.html"


class ResetPasswordConfirmView(auth_views.PasswordResetConfirmView):
    """
    Password reset confirmation view
    """
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    
    def form_valid(self, form):
        """
        Log successful password reset
        """
        user = form.user
        logger.info(f"Password reset successful for user: {user.username} ({user.email})")
        return super().form_valid(form)


class ResetPasswordCompleteView(auth_views.PasswordResetCompleteView):
    """
    Password reset complete view
    """
    template_name = "accounts/password_reset_complete.html"


# ============================
#  LOGOUT
# ============================
@login_required
@never_cache
def logout_view(request):
    """
    User logout view
    """
    user = request.user
    logout(request)
    logger.info(f"User logged out: {user.username if hasattr(user, 'username') else 'Unknown'}")
    messages.success(request, "Bạn đã đăng xuất thành công!")
    return redirect("accounts:login")


# ============================
#  DASHBOARD
# ============================
@login_required
def user_dashboard(request):
    """
    User dashboard view
    """
    user = request.user
    context = {
        "user": user,
    }
    return render(request, "accounts/user_dashboard.html", context)
