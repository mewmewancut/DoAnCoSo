"""Business logic for PDF data preparation and export summaries."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Any

from django.db.models import QuerySet
from django.utils import timezone

from ..models import Task


class PDFService:
    """Prepares task data and statistics for PDF export."""

    @staticmethod
    def get_week_tasks(user) -> dict[str, Any]:
        """Return tasks for the current week with date range."""
        today = timezone.now().date()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

        tasks = Task.objects.filter(
            user=user, deadline__date__range=(start, end)
        ).order_by("deadline")

        return {"tasks": tasks, "start": start, "end": end}

    @staticmethod
    def get_month_tasks(user) -> dict[str, Any]:
        """Return tasks for the current month with date range."""
        today = timezone.now().date()
        start = date(today.year, today.month, 1)
        end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

        tasks = Task.objects.filter(
            user=user, deadline__date__range=(start, end)
        ).order_by("deadline")

        return {"tasks": tasks, "start": start, "end": end}

    @staticmethod
    def get_pdf_data(user, pdf_type: str = "week") -> dict[str, Any]:
        """Build complete PDF export payload (tasks, template, filename)."""
        today = timezone.now().date()

        if pdf_type == "month":
            year, month = today.year, today.month
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            template = "tasks/pdf/month.html"
            filename = f"tasks_month_{month}_{year}.pdf"
        else:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            template = "tasks/pdf/week.html"
            filename = f"tasks_week_{start}_{end}.pdf"

        tasks = Task.objects.filter(
            user=user, deadline__range=(start, end)
        ).order_by("deadline")

        return {
            "tasks": tasks,
            "start": start,
            "end": end,
            "template": template,
            "filename": filename,
        }

    @staticmethod
    def get_custom_range_tasks(user, start_date: date, end_date: date) -> dict[str, Any]:
        """Return tasks within an arbitrary date range."""
        tasks = Task.objects.filter(
            user=user, deadline__date__range=(start_date, end_date)
        ).order_by("deadline")

        return {"tasks": tasks, "start": start_date, "end": end_date}

    @staticmethod
    def get_task_summary_for_pdf(tasks: QuerySet[Task]) -> dict[str, Any]:
        """Generate aggregate statistics for a PDF cover page."""
        total = tasks.count()
        completed = tasks.filter(status="completed").count()
        pending = tasks.filter(status="pending").count()
        in_progress = tasks.filter(status="in_progress").count()

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
            "high_priority": tasks.filter(priority="high").count(),
            "medium_priority": tasks.filter(priority="medium").count(),
            "low_priority": tasks.filter(priority="low").count(),
        }