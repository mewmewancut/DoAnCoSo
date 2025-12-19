import uuid
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import views as auth_views

from .forms import RegisterForm
from .models import Activation

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# ============================
#  ĐĂNG KÝ + GỬI MAIL KÍCH HOẠT
# ============================
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.is_active = False
            user.save()

            # Tạo token kích hoạt CHUẨN Django
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_link = f"http://127.0.0.1:8000/accounts/activate/{uid}/{token}"

            # Gửi email HTML
            html_content = render_to_string(
                "accounts/activation_email.html",
                {"user": user, "activation_link": activation_link}
            )
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject="Kích hoạt tài khoản - ToDo App",
                body=text_content,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            messages.success(request, "Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})




# ============================
#  KÍCH HOẠT TÀI KHOẢN
# ============================
from django.utils.http import urlsafe_base64_decode
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Kích hoạt tài khoản thành công! Hãy đăng nhập.")
        return redirect("login")
    else:
        messages.error(request, "Link kích hoạt không hợp lệ hoặc đã hết hạn.")
        return redirect("register")

# ============================
#  ĐĂNG NHẬP
# ============================
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect("user_dashboard")
            else:
                messages.error(request, "Tài khoản chưa kích hoạt!")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu")

    return render(request, "accounts/login.html")


# ============================
#  QUÊN MẬT KHẨU (4 bước chuẩn Django)
# ============================

class ResetPasswordView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("password_reset_done")


class ResetPasswordDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class ResetPasswordConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class ResetPasswordCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"

from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect('login')
from django.contrib.auth.decorators import login_required
@login_required
def user_dashboard(request):
    return render(request, "accounts/user_dashboard.html")