"""Business logic for SubTask operations."""

from __future__ import annotations

from typing import Any

from django.db.models import Max, QuerySet
from django.utils import timezone

from ..models import SubTask, Task


class SubtaskService:
    """Handles SubTask CRUD, toggle, reorder, and cascade completion."""

    @staticmethod
    def get_subtasks_for_task(task: Task) -> QuerySet[SubTask]:
        return task.subtasks.all()

    @staticmethod
    def get_subtask_by_id(subtask_id, user) -> SubTask | None:
        return SubTask.objects.filter(
            id=subtask_id, task__user=user
        ).select_related("task").first()

    @staticmethod
    def create_subtask(task: Task, title: str, description: str = "") -> SubTask:
        max_order = task.subtasks.aggregate(Max("order"))["order__max"] or 0
        return SubTask.objects.create(
            task=task, title=title, description=description, order=max_order + 1
        )

    @staticmethod
    def create_bulk_subtasks(task: Task, subtask_titles: list[str]) -> list[SubTask]:
        max_order = task.subtasks.aggregate(Max("order"))["order__max"] or 0
        created = []
        for i, title in enumerate(subtask_titles, start=1):
            subtask = SubTask.objects.create(
                task=task, title=title.strip(), order=max_order + i
            )
            created.append(subtask)
        return created

    @staticmethod
    def update_subtask(
        subtask: SubTask,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        order: int | None = None,
    ) -> SubTask:
        if title is not None:
            subtask.title = title.strip()
        if description is not None:
            subtask.description = description.strip()
        if status is not None:
            subtask.status = status
        if order is not None:
            subtask.order = order
        subtask.save()

        # Cascade check after any status change
        if status is not None:
            SubtaskService._check_cascade(subtask.task)

        return subtask

    @staticmethod
    def toggle_subtask(subtask: SubTask) -> tuple[SubTask, bool]:
        """Toggle between completed / pending and run cascade check."""
        subtask.status = "pending" if subtask.status == "completed" else "completed"
        subtask.save()
        parent_completed = SubtaskService._check_cascade(subtask.task)
        return subtask, parent_completed

    @staticmethod
    def _check_cascade(task: Task) -> bool:
        """Mark parent task completed if every subtask is done.

        Returns True when the parent was just transitioned to completed.
        """
        all_subtasks = task.subtasks.all()
        total = all_subtasks.count()
        if total == 0:
            return False
        if all(s.status == "completed" for s in all_subtasks):
            if task.status != "completed":
                task.status = "completed"
                task.save()
                return True
        return False

    @staticmethod
    def delete_subtask(subtask: SubTask) -> None:
        subtask.delete()

    @staticmethod
    def reorder_subtasks(task: Task, orders: list[dict[str, Any]]) -> None:
        for item in orders:
            subtask_id = item.get("id")
            new_order = item.get("order")
            if subtask_id and new_order is not None:
                SubTask.objects.filter(id=subtask_id, task=task).update(order=new_order)

    @staticmethod
    def get_subtask_stats(task: Task) -> dict[str, Any]:
        subtasks = task.subtasks.all()
        total = subtasks.count()
        completed = subtasks.filter(status="completed").count()
        pending = subtasks.filter(status="pending").count()
        in_progress = subtasks.filter(status="in_progress").count()
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
        }

    @staticmethod
    def subtask_to_dict(subtask: SubTask, include_timestamps: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": str(subtask.id),
            "title": subtask.title,
            "description": subtask.description,
            "status": subtask.status,
            "order": subtask.order,
            "is_completed": subtask.is_completed,
        }
        if include_timestamps:
            data["created_at"] = subtask.created_at.isoformat() if subtask.created_at else None
            data["updated_at"] = subtask.updated_at.isoformat() if subtask.updated_at else None
            data["completed_at"] = subtask.completed_at.isoformat() if subtask.completed_at else None
        return data