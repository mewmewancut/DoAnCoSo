"""
Unit tests for the Accounts app.

Covers:
    - User model behaviour
    - Registration form validation
    - Authentication views (login, register, profile)
    - Access control (login required for profile pages)
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import RegisterForm, ProfileEditForm

User = get_user_model()


# ===== MODEL TESTS =========================================================

class UserModelTest(TestCase):
    """Custom User model tests."""

    def test_create_user(self):
        user = User.objects.create_user(
            username="john", email="john@example.com", password="Pass1234!"
        )
        self.assertEqual(user.username, "john")
        self.assertEqual(user.email, "john@example.com")
        self.assertTrue(user.check_password("Pass1234!"))

    def test_uuid_primary_key(self):
        user = User.objects.create_user(
            username="pk_test", email="pk@example.com", password="Pass1234!"
        )
        self.assertIsNotNone(user.id)
        self.assertEqual(len(str(user.id)), 36)  # UUID format

    def test_str(self):
        user = User.objects.create_user(
            username="display", email="d@example.com", password="Pass1234!"
        )
        self.assertIn("display", str(user))
        self.assertIn("d@example.com", str(user))

    def test_get_full_name_or_username_without_names(self):
        user = User.objects.create_user(
            username="noname", email="nn@example.com", password="Pass1234!"
        )
        self.assertEqual(user.get_full_name_or_username(), "noname")

    def test_get_full_name_or_username_with_names(self):
        user = User.objects.create_user(
            username="named", email="named@example.com", password="Pass1234!",
            first_name="John", last_name="Doe"
        )
        self.assertEqual(user.get_full_name_or_username(), "John Doe")

    def test_is_account_activated(self):
        user = User.objects.create_user(
            username="active", email="a@example.com", password="Pass1234!",
            is_active=True,
        )
        self.assertTrue(user.is_account_activated())

    def test_get_avatar_url_none_by_default(self):
        user = User.objects.create_user(
            username="noavatar", email="na@example.com", password="Pass1234!"
        )
        self.assertIsNone(user.get_avatar_url())

    def test_get_display_name_fallback(self):
        user = User.objects.create_user(
            username="fallback", email="fb@example.com", password="Pass1234!"
        )
        self.assertEqual(user.get_display_name(), "fallback")


# ===== FORM TESTS ==========================================================

class RegisterFormTest(TestCase):
    """RegisterForm validation."""

    def test_valid_registration(self):
        form = RegisterForm(data={
            "email": "new@example.com",
            "username": "newuser",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
        })
        self.assertTrue(form.is_valid())

    def test_email_required(self):
        form = RegisterForm(data={
            "username": "user1",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username="existing", email="dup@example.com", password="Pass1234!"
        )
        form = RegisterForm(data={
            "email": "dup@example.com",
            "username": "newname",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_username_rejected(self):
        User.objects.create_user(
            username="taken", email="taken@example.com", password="Pass1234!"
        )
        form = RegisterForm(data={
            "email": "fresh@example.com",
            "username": "taken",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_password_mismatch_rejected(self):
        form = RegisterForm(data={
            "email": "mm@example.com",
            "username": "mismatched",
            "password1": "StrongPass99!",
            "password2": "DifferentPass!",
        })
        self.assertFalse(form.is_valid())

    def test_email_normalised_to_lowercase(self):
        form = RegisterForm(data={
            "email": "TEST@Example.COM",
            "username": "lowercase",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "test@example.com")


class ProfileEditFormTest(TestCase):
    """ProfileEditForm validation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="profile", email="p@example.com", password="Pass1234!"
        )

    def test_valid_edit(self):
        form = ProfileEditForm(
            data={"username": "profile", "first_name": "Test", "last_name": "User"},
            instance=self.user,
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_username_conflict_rejected(self):
        User.objects.create_user(
            username="taken2", email="t2@example.com", password="Pass1234!"
        )
        form = ProfileEditForm(
            data={"username": "taken2"},
            instance=self.user,
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


# ===== VIEW TESTS ==========================================================

class AuthViewTest(TestCase):
    """Authentication views: register, login, logout."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="AuthPass123!",
            is_active=True,
        )

    def test_register_page_loads(self):
        resp = self.client.get(reverse("accounts:register"))
        self.assertEqual(resp.status_code, 200)

    def test_login_page_loads(self):
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 200)

    def test_login_with_valid_credentials(self):
        resp = self.client.post(reverse("accounts:login"), {
            "username": "authuser",
            "password": "AuthPass123!",
        })
        self.assertEqual(resp.status_code, 302)  # redirect to dashboard

    def test_login_with_invalid_password(self):
        resp = self.client.post(reverse("accounts:login"), {
            "username": "authuser",
            "password": "WrongPass!",
        })
        self.assertEqual(resp.status_code, 200)  # re-renders login page

    def test_logout_redirects(self):
        self.client.login(username="authuser", password="AuthPass123!")
        resp = self.client.get(reverse("accounts:logout"))
        self.assertEqual(resp.status_code, 302)

    def test_authenticated_user_redirected_from_register(self):
        self.client.login(username="authuser", password="AuthPass123!")
        resp = self.client.get(reverse("accounts:register"))
        self.assertEqual(resp.status_code, 302)

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username="authuser", password="AuthPass123!")
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 302)


class ProfileViewTest(TestCase):
    """Profile views require login."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="profuser",
            email="prof@example.com",
            password="ProfPass123!",
            is_active=True,
        )

    def _assert_redirects_to_login(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_profile_requires_login(self):
        self._assert_redirects_to_login(reverse("accounts:profile"))

    def test_profile_edit_requires_login(self):
        self._assert_redirects_to_login(reverse("accounts:profile_edit"))

    def test_password_change_requires_login(self):
        self._assert_redirects_to_login(reverse("accounts:password_change"))

    def test_account_delete_requires_login(self):
        self._assert_redirects_to_login(reverse("accounts:account_delete"))

    def test_profile_loads_when_logged_in(self):
        self.client.login(username="profuser", password="ProfPass123!")
        resp = self.client.get(reverse("accounts:profile"))
        self.assertEqual(resp.status_code, 200)

    def test_profile_edit_loads_when_logged_in(self):
        self.client.login(username="profuser", password="ProfPass123!")
        resp = self.client.get(reverse("accounts:profile_edit"))
        self.assertEqual(resp.status_code, 200)

    def test_password_change_loads_when_logged_in(self):
        self.client.login(username="profuser", password="ProfPass123!")
        resp = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(resp.status_code, 200)
