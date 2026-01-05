from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    Enhanced registration form with email validation
    """
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email của bạn',
            'autocomplete': 'email',
        }),
        help_text="Email sẽ được dùng để kích hoạt tài khoản và khôi phục mật khẩu."
    )
    
    username = forms.CharField(
        label="Tên đăng nhập",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập',
            'autocomplete': 'username',
        }),
        help_text="Bắt buộc. 150 ký tự trở xuống. Chỉ chứa chữ cái, số và @/./+/-/_.",
        min_length=3,
        max_length=150,
    )
    
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
            'autocomplete': 'new-password',
        }),
        help_text="Mật khẩu phải có ít nhất 8 ký tự và không được quá giống thông tin cá nhân.",
    )
    
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu',
            'autocomplete': 'new-password',
        }),
        help_text="Nhập lại mật khẩu để xác nhận.",
    )
    
    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")
    
    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    "Email này đã được sử dụng. Vui lòng chọn email khác hoặc đăng nhập."
                )
        return email
    
    def clean_username(self):
        """
        Validate username
        """
        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if User.objects.filter(username=username).exists():
                raise ValidationError(
                    "Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác."
                )
        return username
    
    def save(self, commit=True):
        """
        Save user with normalized email
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        if commit:
            user.save()
        return user
