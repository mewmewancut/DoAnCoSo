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
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        }),
        help_text="Email will be used for account activation and password recovery."
    )
    
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        }),
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        min_length=3,
        max_length=150,
    )
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'new-password',
        }),
        help_text="Password must be at least 8 characters and not too similar to personal information.",
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password again',
            'autocomplete': 'new-password',
        }),
        help_text="Enter your password again to confirm.",
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
                    "Email has already been used. Please choose another one."
                )
        return email
    
    def clean_username(self):

        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if User.objects.filter(username=username).exists():
                raise ValidationError(
                    "Username is already taken. Please choose another one."
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
            'placeholder': 'Enter your username',
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
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name',
        }),
        max_length=150,
    )
    
    last_name = forms.CharField(
        label="Tên",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
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
        help_text="Upload your avatar (JPG, PNG, GIF - max 5MB)",
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
                    "Username is already taken. Please choose another one."
                )
        return username


class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password',
        }),
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password',
        }),
        help_text="Password must be at least 8 characters and not too similar to personal information.",
    )
    
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password again',
            'autocomplete': 'new-password',
        }),
        help_text="Enter your password again to confirm.",
    )
