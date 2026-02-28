"""Business logic for task statistics and progress tracking."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Avg, F, QuerySet
from django.utils import timezone

from ..models import Task


class StatisticsService:
    """Generates aggregate statistics from user task data."""

    @staticmethod
    def get_overview_stats(user) -> dict[str, Any]:
        """Return count-based overview for a user."""
        tasks: QuerySet[Task] = Task.objects.filter(user=user)
        total = tasks.count()
        completed = tasks.filter(status="completed").count()
        pending = tasks.filter(status="pending").count()
        in_progress = tasks.filter(status="in_progress").count()
        cancelled = tasks.filter(status="cancelled").count()

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "cancelled_tasks": cancelled,
            "completion_rate": round(completed / total * 100, 2) if total else 0,
        }

    @staticmethod
    def get_overdue_stats(user) -> dict[str, Any]:
        """Return overdue tasks using a DB-level filter (avoids Python loop)."""
        now = timezone.now()
        overdue_qs = Task.objects.filter(
            user=user,
            deadline__lt=now,
            status__in=["pending", "in_progress"],
        ).order_by("deadline")

        return {
            "count": overdue_qs.count(),
            "tasks": list(overdue_qs),
        }

    @staticmethod
    def get_priority_stats(user) -> dict[str, int]:
        """Return task counts grouped by priority level."""
        tasks = Task.objects.filter(user=user)
        return {
            "high": tasks.filter(priority="high").count(),
            "medium": tasks.filter(priority="medium").count(),
            "low": tasks.filter(priority="low").count(),
        }

    @staticmethod
    def get_activity_stats(user) -> dict[str, int]:
        """Return creation / completion counts for the last 7 and 30 days."""
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        tasks = Task.objects.filter(user=user)

        return {
            "created_this_week": tasks.filter(created_at__gte=week_ago).count(),
            "created_this_month": tasks.filter(created_at__gte=month_ago).count(),
            "completed_this_week": tasks.filter(
                completed_at__gte=week_ago, completed_at__isnull=False
            ).count(),
            "completed_this_month": tasks.filter(
                completed_at__gte=month_ago, completed_at__isnull=False
            ).count(),
        }

    @staticmethod
    def get_average_completion_time(user) -> float | None:
        """Use a DB aggregate instead of loading every completed task into Python."""
        result = (
            Task.objects.filter(user=user, completed_at__isnull=False)
            .annotate(duration=F("completed_at") - F("created_at"))
            .aggregate(avg=Avg("duration"))
        )
        avg_duration = result["avg"]
        if avg_duration is None:
            return None
        return round(avg_duration.total_seconds() / 86400, 1)

    @staticmethod
    def get_upcoming_deadlines(user) -> dict[str, int]:
        """Count tasks due within the next 7 / 30 days."""
        now = timezone.now()
        active = Task.objects.filter(user=user, status__in=["pending", "in_progress"])
        return {
            "next_7_days": active.filter(
                deadline__gte=now, deadline__lt=now + timedelta(days=7)
            ).count(),
            "next_30_days": active.filter(
                deadline__gte=now, deadline__lt=now + timedelta(days=30)
            ).count(),
        }

    @classmethod
    def get_full_statistics(cls, user) -> dict[str, Any]:
        """Aggregate all statistics for the API response."""
        overview = cls.get_overview_stats(user)
        overdue = cls.get_overdue_stats(user)

        return {
            "overview": {**overview, "overdue_tasks": overdue["count"]},
            "priority_breakdown": cls.get_priority_stats(user),
            "activity": {
                **cls.get_activity_stats(user),
                "avg_completion_days": cls.get_average_completion_time(user),
            },
            "upcoming": cls.get_upcoming_deadlines(user),
        }

    @staticmethod
    def get_dashboard_data(user) -> dict[str, Any]:
        """Optimised dashboard query: DB-level overdue filter, prefetched tags."""
        tasks = Task.objects.filter(user=user)
        now = timezone.now()

        total = tasks.count()
        pending = tasks.filter(status="pending").count()
        in_progress = tasks.filter(status="in_progress").count()
        completed = tasks.filter(status="completed").count()

        overdue_qs = tasks.filter(
            deadline__lt=now,
            status__in=["pending", "in_progress"],
        ).order_by("deadline")

        recent = tasks.prefetch_related("tags")[:5]

        return {
            "total_tasks": total,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "completed_tasks": completed,
            "overdue_tasks": overdue_qs,
            "overdue_count": overdue_qs.count(),
            "recent_tasks": recent,
        }