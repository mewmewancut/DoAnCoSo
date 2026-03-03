from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Nhập địa chỉ email',
            'autocomplete': 'email',
        }),
        help_text="Địa chỉ email sẽ được dùng để kích hoạt tài khoản và khôi phục mật khẩu.",
    )
    
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập tên đăng nhập',
            'autocomplete': 'username',
        }),
        help_text="Bắt buộc. Tối đa 150 ký tự. Chỉ chấp nhận chữ cái, chữ số và các ký tự @/./+/-/_.",
        min_length=3,
        max_length=150,
    )
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu của bạn',
            'autocomplete': 'new-password',
        }),
        help_text="Mật khẩu phải có ít nhất 8 ký tự và không quá giống thông tin cá nhân.",
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu của bạn',
            'autocomplete': 'new-password',
        }),
        help_text="Nhập lại mật khẩu để xác nhận.",
    )
    
    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")
    
    def clean_email(self):

        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    "Email đã được sử dụng. Vui lòng chọn email khác."
                )
        return email
    
    def clean_username(self):

        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if User.objects.filter(username=username).exists():
                raise ValidationError(
                    "Username đã được sử dụng. Vui lòng chọn tên đăng nhập khác."
                )
        return username
    
    def save(self, commit=True):

        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):

    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập của bạn',
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
        label="Avatar",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        help_text="Tải lên ảnh đại diện (JPG, PNG, GIF - tối đa 5MB)",
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'avatar')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):

        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if self.user and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
                raise ValidationError(
                    "Username đã được sử dụng. Vui lòng chọn tên đăng nhập khác."
                )
        return username


class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu hiện tại của bạn',
            'autocomplete': 'current-password',
        }),
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới của bạn',
            'autocomplete': 'new-password',
        }),
        help_text="Mật khẩu phải có ít nhất 8 ký tự và không quá giống thông tin cá nhân.",
    )
    
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu của bạn',
            'autocomplete': 'new-password',
        }),
        help_text="Nhập lại mật khẩu để xác nhận.",
    )

