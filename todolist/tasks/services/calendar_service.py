"""Business logic for calendar views and FullCalendar event generation."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone

from ..models import Task


class CalendarService:
    """Generates event data for FullCalendar and date-ranged task views."""

    @staticmethod
    def get_calendar_events(user) -> list[dict[str, Any]]:
        """Return all tasks with deadlines formatted for FullCalendar."""
        tasks = Task.objects.filter(user=user, deadline__isnull=False)
        return [CalendarService._task_to_event(t) for t in tasks]

    @staticmethod
    def _task_to_event(task: Task) -> dict[str, Any]:
        if task.is_overdue:
            status, color = "overdue", "#dc3545"
        elif task.status == "completed":
            status, color = "completed", "#198754"
        elif task.status == "in_progress":
            status, color = "in_progress", "#ffc107"
        else:
            status, color = "pending", "#0d6efd"

        return {
            "id": str(task.id),
            "title": task.title,
            "start": timezone.localtime(task.deadline).isoformat(),
            "url": f"/tasks/{task.id}/",
            "color": color,
            "extendedProps": {
                "status": status,
                "status_label": status.replace("_", " ").title(),
                "status_color": color,
                "priority": task.priority,
                "description": task.description or "",
            },
        }

    @staticmethod
    def get_today_data(user) -> dict[str, Any]:
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        return {
            "tasks_today": Task.objects.filter(
                user=user, deadline__gte=today_start, deadline__lt=today_end
            ).order_by("deadline"),
            "overdue_tasks": Task.objects.filter(
                user=user, deadline__lt=now, status__in=["pending", "in_progress"]
            ).order_by("deadline"),
            "completed_today": Task.objects.filter(
                user=user, completed_at__gte=today_start, completed_at__lt=today_end
            ).order_by("-completed_at"),
            "today_date": now.date(),
        }

    @staticmethod
    def get_weekly_data(user) -> dict[str, Any]:
        """Group tasks by day of the current week.

        Evaluates the week queryset once, then partitions in Python to
        avoid 7 separate DB queries.
        """
        now = timezone.now()
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        week_end = week_start + timedelta(days=7)

        all_tasks = list(
            Task.objects.filter(
                user=user, deadline__gte=week_start, deadline__lt=week_end
            ).order_by("deadline")
        )

        days_tasks: dict = {}
        for i in range(7):
            day = (week_start + timedelta(days=i)).date()
            days_tasks[day] = [
                t for t in all_tasks
                if t.deadline and timezone.localtime(t.deadline).date() == day
            ]

        completed_count = sum(1 for t in all_tasks if t.status == "completed")

        return {
            "week_start": week_start.date(),
            # Display end date inclusive (week_end is exclusive bound)
            "week_end": (week_end - timedelta(days=1)).date(),
            "days_tasks": days_tasks,
            "total_tasks": len(all_tasks),
            "completed_tasks": completed_count,
        }

    @staticmethod
    def get_monthly_data(user) -> dict[str, Any]:
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        tasks_this_month = Task.objects.filter(
            user=user, deadline__gte=month_start, deadline__lt=month_end
        ).order_by("deadline")

        all_tasks = list(tasks_this_month)

        weeks_tasks: dict = {}
        current_date = month_start
        week_num = 1
        while current_date < month_end:
            wk_end = current_date + timedelta(days=7)
            wk_tasks = [
                t for t in all_tasks
                if t.deadline and current_date <= t.deadline < wk_end
            ]
            weeks_tasks[f"Week {week_num}"] = {
                "start": current_date.date(),
                # Display end date inclusive (wk_end/month_end are exclusive bounds)
                "end": (min(wk_end, month_end) - timedelta(days=1)).date(),
                "tasks": wk_tasks,
            }
            current_date = wk_end
            week_num += 1

        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.status == "completed")
        progress = round(completed / total * 100) if total else 0

        return {
            "month_start": month_start.date(),
            # Display end date inclusive (month_end is exclusive bound)
            "month_end": (month_end - timedelta(days=1)).date(),
            "weeks_tasks": weeks_tasks,
            "total_tasks": total,
            "completed_tasks": completed,
            "progress_percentage": progress,
        }