from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
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


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user profile information (email cannot be changed)
    """
    username = forms.CharField(
        label="Tên đăng nhập",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập',
            'autocomplete': 'username',
        }),
        min_length=3,
        max_length=150,
    )
    
    first_name = forms.CharField(
        label="Họ",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ của bạn',
            'autocomplete': 'given-name',
        }),
        max_length=150,
    )
    
    last_name = forms.CharField(
        label="Tên",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên của bạn',
            'autocomplete': 'family-name',
        }),
        max_length=150,
    )
    
    avatar = forms.ImageField(
        label="Ảnh đại diện",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        help_text="Upload ảnh đại diện của bạn (JPG, PNG, GIF - tối đa 5MB)",
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'avatar')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        """
        Validate username uniqueness (excluding current user)
        """
        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if self.user and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
                raise ValidationError(
                    "Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác."
                )
        return username


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with better styling
    """
    old_password = forms.CharField(
        label="Mật khẩu hiện tại",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu hiện tại',
            'autocomplete': 'current-password',
        }),
    )
    
    new_password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới',
            'autocomplete': 'new-password',
        }),
        help_text="Mật khẩu phải có ít nhất 8 ký tự và không được quá giống thông tin cá nhân.",
    )
    
    new_password2 = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu mới',
            'autocomplete': 'new-password',
        }),
        help_text="Nhập lại mật khẩu mới để xác nhận.",
    )
