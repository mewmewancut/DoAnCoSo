"""Business logic for Task CRUD operations."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.utils import timezone

from ..models import Task


class TaskService:
    """Encapsulates Task query logic, keeping views thin."""

    VALID_SORTS: list[str] = [
        "created_at", "-created_at",
        "deadline", "-deadline",
        "priority", "-priority",
        "status", "-status",
        "title", "-title",
    ]

    @staticmethod
    def get_user_tasks(user) -> QuerySet[Task]:
        return Task.objects.filter(user=user)

    @staticmethod
    def get_task_by_id(task_id, user) -> Task | None:
        return Task.objects.filter(id=task_id, user=user).first()

    @classmethod
    def get_filtered_tasks(
        cls,
        user,
        status: str | None = None,
        priority: str | None = None,
        deadline_filter: str | None = None,
    ) -> QuerySet[Task]:
        """Apply optional status / priority / deadline filters."""
        tasks = cls.get_user_tasks(user)
        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if deadline_filter:
            tasks = cls._apply_deadline_filter(tasks, deadline_filter)
        return tasks

    @staticmethod
    def _apply_deadline_filter(tasks: QuerySet[Task], deadline_filter: str) -> QuerySet[Task]:
        now = timezone.now()
        if deadline_filter == "overdue":
            return tasks.filter(deadline__lt=now).exclude(status="completed")
        if deadline_filter == "today":
            return tasks.filter(deadline__date=now.date())
        if deadline_filter == "week":
            return tasks.filter(deadline__gte=now, deadline__lte=now + timedelta(days=7))
        if deadline_filter == "month":
            return tasks.filter(deadline__gte=now, deadline__lte=now + timedelta(days=30))
        return tasks

    @classmethod
    def get_sorted_tasks(cls, tasks: QuerySet[Task], sort_by: str = "-created_at") -> QuerySet[Task]:
        if sort_by not in cls.VALID_SORTS:
            sort_by = "-created_at"
        if sort_by in ("deadline", "-deadline"):
            return tasks.order_by(sort_by, "created_at")
        return tasks.order_by(sort_by)

    @staticmethod
    def paginate_tasks(tasks: QuerySet[Task], page: int = 1, per_page: int = 10) -> tuple[Page, Paginator]:
        paginator = Paginator(tasks, per_page)
        try:
            paginated = paginator.page(page)
        except PageNotAnInteger:
            paginated = paginator.page(1)
        except EmptyPage:
            paginated = paginator.page(paginator.num_pages)
        return paginated, paginator

    @staticmethod
    def create_task(
        user,
        title: str,
        description: str | None = None,
        deadline=None,
        priority: str = "medium",
        status: str = "pending",
    ) -> Task:
        return Task.objects.create(
            user=user,
            title=title,
            description=description,
            deadline=deadline or None,
            priority=priority,
            status=status,
        )

    @staticmethod
    def update_task(
        task: Task,
        title: str,
        description: str | None = None,
        deadline=None,
        priority: str = "medium",
        status: str = "pending",
    ) -> Task:
        task.title = title
        task.description = description
        task.deadline = deadline or None
        task.priority = priority
        task.status = status
        task.save()
        return task

    @staticmethod
    def update_task_status(task: Task, new_status: str) -> Task:
        task.status = new_status
        task.save()
        return task

    @staticmethod
    def delete_task(task: Task) -> None:
        task.delete()

    @staticmethod
    def get_overdue_tasks(user) -> QuerySet[Task]:
        now = timezone.now()
        return Task.objects.filter(
            user=user, deadline__lt=now, status__in=["pending", "in_progress"]
        ).order_by("deadline")

    @staticmethod
    def get_tasks_for_date(user, target_date) -> QuerySet[Task]:
        return Task.objects.filter(user=user, deadline__date=target_date).order_by("deadline")

    @staticmethod
    def get_tasks_for_date_range(user, start_date, end_date) -> QuerySet[Task]:
        return Task.objects.filter(
            user=user, deadline__gte=start_date, deadline__lt=end_date
        ).order_by("deadline")

    @staticmethod
    def get_completed_tasks_for_date_range(user, start_date, end_date) -> QuerySet[Task]:
        return Task.objects.filter(
            user=user, completed_at__gte=start_date, completed_at__lt=end_date
        ).order_by("-completed_at")

    @staticmethod
    def get_recent_tasks(user, limit: int = 5) -> QuerySet[Task]:
        return Task.objects.filter(user=user)[:limit]

    @staticmethod
    def calculate_task_progress(task: Task) -> dict[str, Any]:
        """Return subtask completion stats for a single task."""
        subtasks = task.subtasks.all()
        total = subtasks.count()
        completed = subtasks.filter(status="completed").count()
        percentage = (completed / total * 100) if total else 0
        return {
            "total": total,
            "completed": completed,
            "percentage": round(percentage, 1),
        }