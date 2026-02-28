"""
Unit tests for the Tasks app.

Covers:
    - Model behaviour (Task, SubTask, Tag, AISuggestion)
    - Form validation (TaskForm deadline, required fields)
    - View access control and CRUD workflows
    - Service-layer logic (TaskService, SubtaskService)
"""

import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TaskForm
from .models import AISuggestion, SubTask, Tag, Task
from .services import SubtaskService, TaskService

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _BaseTestCase(TestCase):
    """Shared setUp for all Task-related tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
            is_active=True,
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="OtherPass123!",
            is_active=True,
        )
        self.client = Client()
        self.client.login(username="testuser", password="TestPass123!")


# ===== MODEL TESTS =========================================================

class TagModelTest(TestCase):
    """Tag model: slug auto-generation, __str__."""

    def test_slug_auto_generated(self):
        tag = Tag.objects.create(name="My Tag")
        self.assertEqual(tag.slug, "my-tag")

    def test_str(self):
        tag = Tag.objects.create(name="Work")
        self.assertEqual(str(tag), "Work")


class TaskModelTest(_BaseTestCase):
    """Task model: save() completed_at tracking, is_overdue, days_to_deadline."""

    def _create_task(self, **kwargs):
        defaults = {
            "user": self.user,
            "title": "Test Task",
            "priority": "medium",
            "status": "pending",
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    # --- save() auto-sets completed_at ---

    def test_completed_at_set_on_completion(self):
        task = self._create_task(status="pending")
        self.assertIsNone(task.completed_at)

        task.status = "completed"
        task.save()
        task.refresh_from_db()
        self.assertIsNotNone(task.completed_at)

    def test_completed_at_cleared_when_reopened(self):
        task = self._create_task(status="completed")
        self.assertIsNotNone(task.completed_at)

        task.status = "pending"
        task.save()
        task.refresh_from_db()
        self.assertIsNone(task.completed_at)

    # --- is_overdue ---

    def test_is_overdue_true(self):
        task = self._create_task(
            deadline=timezone.now() - timedelta(days=1),
            status="pending",
        )
        self.assertTrue(task.is_overdue)

    def test_is_overdue_false_when_completed(self):
        task = self._create_task(
            deadline=timezone.now() - timedelta(days=1),
            status="completed",
        )
        self.assertFalse(task.is_overdue)

    def test_is_overdue_false_future_deadline(self):
        task = self._create_task(
            deadline=timezone.now() + timedelta(days=5),
            status="pending",
        )
        self.assertFalse(task.is_overdue)

    def test_is_overdue_false_no_deadline(self):
        task = self._create_task(status="pending")
        self.assertFalse(task.is_overdue)

    # --- days_to_deadline ---

    def test_days_to_deadline_returns_int(self):
        task = self._create_task(deadline=timezone.now() + timedelta(days=3))
        self.assertIsInstance(task.days_to_deadline, int)

    def test_days_to_deadline_none_without_deadline(self):
        task = self._create_task()
        self.assertIsNone(task.days_to_deadline)

    # --- completion_time ---

    def test_completion_time_returns_timedelta(self):
        task = self._create_task(status="completed")
        self.assertIsNotNone(task.completion_time)

    # --- __str__ ---

    def test_str(self):
        task = self._create_task(title="Sample Title")
        self.assertEqual(str(task), "Sample Title")


class SubTaskModelTest(_BaseTestCase):
    """SubTask model: save() completed_at tracking, is_completed."""

    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            user=self.user, title="Parent", status="pending"
        )

    def test_completed_at_set_on_completion(self):
        sub = SubTask.objects.create(task=self.task, title="Sub1", status="pending")
        sub.status = "completed"
        sub.save()
        sub.refresh_from_db()
        self.assertIsNotNone(sub.completed_at)

    def test_completed_at_cleared_on_reopen(self):
        sub = SubTask.objects.create(task=self.task, title="Sub1", status="completed")
        sub.status = "pending"
        sub.save()
        sub.refresh_from_db()
        self.assertIsNone(sub.completed_at)

    def test_is_completed_property(self):
        sub = SubTask.objects.create(task=self.task, title="Sub1", status="completed")
        self.assertTrue(sub.is_completed)

    def test_str(self):
        sub = SubTask.objects.create(task=self.task, title="Sub1")
        self.assertIn("Parent", str(sub))
        self.assertIn("Sub1", str(sub))


class AISuggestionModelTest(_BaseTestCase):
    """AISuggestion model: str, suggestion types."""

    def test_str_contains_type(self):
        task = Task.objects.create(user=self.user, title="T")
        suggestion = AISuggestion.objects.create(
            task=task,
            user=self.user,
            suggestion_type="description",
            input_data={"text": "test"},
            output_data={"result": "improved"},
        )
        self.assertIn("Description Improvement", str(suggestion))

    def test_wizard_type_accepted(self):
        suggestion = AISuggestion.objects.create(
            user=self.user,
            suggestion_type="wizard",
            input_data={},
            output_data={},
        )
        self.assertEqual(suggestion.suggestion_type, "wizard")


# ===== FORM TESTS ==========================================================

class TaskFormTest(TestCase):
    """TaskForm: validation — deadline, required fields."""

    def test_valid_form(self):
        form = TaskForm(data={
            "title": "My Task",
            "priority": "medium",
            "status": "pending",
        })
        self.assertTrue(form.is_valid())

    def test_title_required(self):
        form = TaskForm(data={
            "priority": "medium",
            "status": "pending",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_deadline_in_past_rejected_for_new_task(self):
        # Use localtime so the formatted string matches what Django parses back
        past = (timezone.localtime() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
        form = TaskForm(data={
            "title": "Past Deadline",
            "deadline": past,
            "priority": "medium",
            "status": "pending",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("deadline", form.errors)

    def test_deadline_in_future_accepted(self):
        future = (timezone.localtime() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        form = TaskForm(data={
            "title": "Future Deadline",
            "deadline": future,
            "priority": "medium",
            "status": "pending",
        })
        self.assertTrue(form.is_valid())

    def test_deadline_in_past_allowed_for_existing_task(self):
        """Editing an existing task should allow past deadlines."""
        user = User.objects.create_user(
            username="formtester", email="ft@example.com", password="pass123!"
        )
        task = Task.objects.create(
            user=user, title="Old", priority="low", status="pending",
        )
        past = (timezone.localtime() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
        form = TaskForm(
            data={
                "title": "Updated",
                "deadline": past,
                "priority": "medium",
                "status": "pending",
            },
            instance=task,
        )
        self.assertTrue(form.is_valid())

    def test_invalid_priority_rejected(self):
        form = TaskForm(data={
            "title": "Bad Priority",
            "priority": "urgent",
            "status": "pending",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("priority", form.errors)


# ===== VIEW TESTS ==========================================================

class AuthRequiredViewTest(TestCase):
    """All task views require login — unauthenticated users get redirected."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser",
            email="view@example.com",
            password="ViewPass123!",
            is_active=True,
        )
        self.task = Task.objects.create(
            user=self.user, title="T", status="pending"
        )

    def _assert_redirects_to_login(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_task_list_requires_login(self):
        self._assert_redirects_to_login(reverse("tasks:task_list"))

    def test_task_create_requires_login(self):
        self._assert_redirects_to_login(reverse("tasks:task_create"))

    def test_task_detail_requires_login(self):
        self._assert_redirects_to_login(
            reverse("tasks:task_detail", args=[self.task.id])
        )

    def test_task_update_requires_login(self):
        self._assert_redirects_to_login(
            reverse("tasks:task_update", args=[self.task.id])
        )

    def test_task_delete_requires_login(self):
        self._assert_redirects_to_login(
            reverse("tasks:task_delete", args=[self.task.id])
        )

    def test_dashboard_requires_login(self):
        self._assert_redirects_to_login(reverse("tasks:dashboard"))

    def test_ai_assistant_requires_login(self):
        self._assert_redirects_to_login(reverse("tasks:ai_assistant"))


class TaskCRUDViewTest(_BaseTestCase):
    """Full CRUD cycle via the web views."""

    def test_task_list_status_200(self):
        resp = self.client.get(reverse("tasks:task_list"))
        self.assertEqual(resp.status_code, 200)

    def test_task_create_get(self):
        resp = self.client.get(reverse("tasks:task_create"))
        self.assertEqual(resp.status_code, 200)

    def test_task_create_post(self):
        resp = self.client.post(reverse("tasks:task_create"), {
            "title": "New Task",
            "priority": "high",
            "status": "pending",
        })
        self.assertEqual(resp.status_code, 302)  # redirect on success
        self.assertTrue(Task.objects.filter(title="New Task").exists())

    def test_task_detail(self):
        task = Task.objects.create(user=self.user, title="Detail", status="pending")
        resp = self.client.get(reverse("tasks:task_detail", args=[task.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Detail")

    def test_task_update_post(self):
        task = Task.objects.create(user=self.user, title="Old Title", status="pending")
        resp = self.client.post(
            reverse("tasks:task_update", args=[task.id]),
            {"title": "New Title", "priority": "low", "status": "in_progress"},
        )
        self.assertEqual(resp.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, "New Title")

    def test_task_delete_post(self):
        task = Task.objects.create(user=self.user, title="Delete Me", status="pending")
        resp = self.client.post(reverse("tasks:task_delete", args=[task.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_cannot_view_other_users_task(self):
        other_task = Task.objects.create(
            user=self.other_user, title="Secret", status="pending"
        )
        resp = self.client.get(reverse("tasks:task_detail", args=[other_task.id]))
        self.assertEqual(resp.status_code, 404)

    def test_dashboard_status_200(self):
        resp = self.client.get(reverse("tasks:dashboard"))
        self.assertEqual(resp.status_code, 200)


class TaskQuickStatusViewTest(_BaseTestCase):
    """AJAX quick-status endpoint tests."""

    def test_quick_status_valid(self):
        task = Task.objects.create(user=self.user, title="QS", status="pending")
        resp = self.client.post(
            reverse("tasks:task_quick_status", args=[task.id]),
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        task.refresh_from_db()
        self.assertEqual(task.status, "completed")

    def test_quick_status_invalid_value(self):
        task = Task.objects.create(user=self.user, title="QS2", status="pending")
        resp = self.client.post(
            reverse("tasks:task_quick_status", args=[task.id]),
            data=json.dumps({"status": "invalid"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_quick_status_wrong_method(self):
        task = Task.objects.create(user=self.user, title="QS3", status="pending")
        resp = self.client.get(reverse("tasks:task_quick_status", args=[task.id]))
        self.assertEqual(resp.status_code, 405)


class TaskFilterSortViewTest(_BaseTestCase):
    """Filtering and sorting via query parameters."""

    def test_filter_by_status(self):
        Task.objects.create(user=self.user, title="A", status="pending")
        Task.objects.create(user=self.user, title="B", status="completed")
        resp = self.client.get(reverse("tasks:task_list") + "?status=pending")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "A")

    def test_sort_by_title(self):
        Task.objects.create(user=self.user, title="Zebra", status="pending")
        Task.objects.create(user=self.user, title="Apple", status="pending")
        resp = self.client.get(reverse("tasks:task_list") + "?sort=title")
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertTrue(content.index("Apple") < content.index("Zebra"))


# ===== SERVICE TESTS ========================================================

class TaskServiceTest(_BaseTestCase):
    """TaskService static methods."""

    def test_get_user_tasks(self):
        Task.objects.create(user=self.user, title="Mine")
        Task.objects.create(user=self.other_user, title="Theirs")
        qs = TaskService.get_user_tasks(self.user)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().title, "Mine")

    def test_get_filtered_tasks_by_priority(self):
        Task.objects.create(user=self.user, title="H", priority="high")
        Task.objects.create(user=self.user, title="L", priority="low")
        qs = TaskService.get_filtered_tasks(self.user, priority="high")
        self.assertEqual(qs.count(), 1)

    def test_get_sorted_tasks_invalid_falls_back(self):
        Task.objects.create(user=self.user, title="X")
        qs = TaskService.get_user_tasks(self.user)
        sorted_qs = TaskService.get_sorted_tasks(qs, "INVALID")
        self.assertEqual(sorted_qs.count(), 1)  # still returns results

    def test_paginate_tasks(self):
        for i in range(15):
            Task.objects.create(user=self.user, title=f"T{i}")
        qs = TaskService.get_user_tasks(self.user)
        page, paginator = TaskService.paginate_tasks(qs, page=1, per_page=10)
        self.assertEqual(len(page), 10)
        self.assertEqual(paginator.num_pages, 2)

    def test_create_task(self):
        task = TaskService.create_task(self.user, title="Service Task")
        self.assertEqual(task.title, "Service Task")
        self.assertEqual(task.user, self.user)

    def test_calculate_task_progress(self):
        task = Task.objects.create(user=self.user, title="Prog")
        SubTask.objects.create(task=task, title="S1", status="completed")
        SubTask.objects.create(task=task, title="S2", status="pending")
        progress = TaskService.calculate_task_progress(task)
        self.assertEqual(progress["total"], 2)
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["percentage"], 50)


class SubtaskServiceTest(_BaseTestCase):
    """SubtaskService operations."""

    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(user=self.user, title="Parent", status="pending")

    def test_create_subtask(self):
        sub = SubtaskService.create_subtask(self.task, "Sub 1")
        self.assertEqual(sub.title, "Sub 1")
        self.assertEqual(sub.task, self.task)

    def test_create_bulk_subtasks(self):
        subs = SubtaskService.create_bulk_subtasks(self.task, ["A", "B", "C"])
        self.assertEqual(len(subs), 3)
        self.assertEqual(self.task.subtasks.count(), 3)

    def test_toggle_subtask(self):
        sub = SubtaskService.create_subtask(self.task, "Toggle Me")
        self.assertEqual(sub.status, "pending")
        sub, _ = SubtaskService.toggle_subtask(sub)
        self.assertEqual(sub.status, "completed")
        sub, _ = SubtaskService.toggle_subtask(sub)
        self.assertEqual(sub.status, "pending")

    def test_cascade_completion(self):
        """All subtasks completed -> parent task auto-completes."""
        sub1 = SubtaskService.create_subtask(self.task, "S1")
        sub2 = SubtaskService.create_subtask(self.task, "S2")
        SubtaskService.toggle_subtask(sub1)
        _, parent_completed = SubtaskService.toggle_subtask(sub2)
        self.assertTrue(parent_completed)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")

    def test_update_subtask(self):
        sub = SubtaskService.create_subtask(self.task, "Old")
        SubtaskService.update_subtask(sub, title="New", status="in_progress")
        sub.refresh_from_db()
        self.assertEqual(sub.title, "New")
        self.assertEqual(sub.status, "in_progress")

    def test_delete_subtask(self):
        sub = SubtaskService.create_subtask(self.task, "Delete Me")
        sid = sub.id
        SubtaskService.delete_subtask(sub)
        self.assertFalse(SubTask.objects.filter(id=sid).exists())

    def test_reorder_subtasks(self):
        s1 = SubtaskService.create_subtask(self.task, "First")
        s2 = SubtaskService.create_subtask(self.task, "Second")
        SubtaskService.reorder_subtasks(
            self.task,
            [{"id": str(s2.id), "order": 0}, {"id": str(s1.id), "order": 1}]
        )
        s1.refresh_from_db()
        s2.refresh_from_db()
        self.assertEqual(s2.order, 0)
        self.assertEqual(s1.order, 1)
