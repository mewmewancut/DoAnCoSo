"""Views for the Tasks app  delegates business logic to the service layer."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from .forms import TaskForm
from .models import SubTask, Tag, Task
from .services import (
    CalendarService,
    PDFService,
    StatisticsService,
    SubtaskService,
    TaskService,
)


@login_required
def task_list(request):
    """Display all tasks for the current user with filters, sorting and pagination."""
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    deadline_filter = request.GET.get("deadline")
    tag_filter = request.GET.get("tag")
    sort_by = request.GET.get("sort", "-created_at")
    page = request.GET.get("page", 1)

    tasks = TaskService.get_filtered_tasks(
        user=request.user,
        status=status_filter,
        priority=priority_filter,
        deadline_filter=deadline_filter,
    )

    if tag_filter:
        tasks = tasks.filter(tags__slug=tag_filter)

    tasks = TaskService.get_sorted_tasks(tasks, sort_by).prefetch_related("tags")
    tasks_page, paginator = TaskService.paginate_tasks(tasks, page)

    context = {
        "tasks": tasks_page,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "deadline_filter": deadline_filter,
        "tag_filter": tag_filter,
        "sort_by": sort_by,
        "paginator": paginator,
        "all_tags": Tag.objects.all(),
    }
    return render(request, "tasks/task_list.html", context)


@login_required
def task_detail(request, task_id):
    """Display a single task with its subtasks and progress."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    subtasks = SubtaskService.get_subtasks_for_task(task)
    progress = TaskService.calculate_task_progress(task)

    context = {
        "task": task,
        "subtasks": subtasks,
        "total_subtasks": progress["total"],
        "completed_subtasks": progress["completed"],
        "progress_percent": progress["percentage"],
    }
    return render(request, "tasks/task_detail.html", context)


@login_required
def task_create(request):
    """Create a new task using Django ModelForm."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            messages.success(
                request,
                _('Task "%(title)s" created successfully!') % {"title": task.title},
            )
            return redirect("tasks:task_detail", task_id=task.id)
    else:
        form = TaskForm()

    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def task_update(request, task_id):
    """Update an existing task using Django ModelForm."""
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                _('Task "%(title)s" updated successfully!') % {"title": task.title},
            )
            return redirect("tasks:task_detail", task_id=task.id)
    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/task_form.html", {"task": task, "form": form})


@login_required
def task_delete(request, task_id):
    """Delete a task after POST confirmation."""
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        task_title = task.title
        TaskService.delete_task(task)
        messages.success(
            request,
            _('Task "%(title)s" deleted successfully!') % {"title": task_title},
        )
        return redirect("tasks:task_list")

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
def task_quick_status(request, task_id):
    """Quick-update task status via AJAX."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": _("Invalid method")}, status=405)

    task = get_object_or_404(Task, id=task_id, user=request.user)
    data = json.loads(request.body)
    new_status = data.get("status")

    if new_status not in ("pending", "in_progress", "completed", "cancelled"):
        return JsonResponse(
            {"success": False, "error": _("Invalid status value")}, status=400
        )

    TaskService.update_task_status(task, new_status)

    return JsonResponse({
        "success": True,
        "task": {
            "id": str(task.id),
            "status": task.status,
            "status_display": task.get_status_display(),
        },
    })


@login_required
def dashboard(request):
    """Main dashboard with task statistics."""
    data = StatisticsService.get_dashboard_data(request.user)
    return render(request, "tasks/dashboard.html", data)


@login_required
def task_calendar(request):
    """Calendar view page."""
    return render(request, "tasks/task_calendar.html")


@login_required
def task_calendar_events(request):
    """API endpoint returning FullCalendar-compatible events."""
    events = CalendarService.get_calendar_events(request.user)
    return JsonResponse(events, safe=False)


@login_required
def today_view(request):
    """Tasks due today."""
    data = CalendarService.get_today_data(request.user)
    return render(request, "tasks/partials/today.html", data)


@login_required
def weekly_view(request):
    """Tasks for the current week."""
    data = CalendarService.get_weekly_data(request.user)
    return render(request, "tasks/partials/weekly_view.html", data)


@login_required
def monthly_view(request):
    """Tasks for the current month."""
    data = CalendarService.get_monthly_data(request.user)
    return render(request, "tasks/partials/monthly_view.html", data)


@login_required
def progress_statistics_api(request):
    """API endpoint returning comprehensive task progress statistics."""
    statistics = StatisticsService.get_full_statistics(request.user)
    return JsonResponse(statistics)


@login_required
def ai_assistant(request):
    """AI Assistant page."""
    return render(request, "tasks/ai_assistant.html")


@login_required
def subtask_create(request, task_id):
    """Create a new subtask (AJAX)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": _("Invalid method")}, status=405)

    task = get_object_or_404(Task, id=task_id, user=request.user)
    data = json.loads(request.body)
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not title:
        return JsonResponse(
            {"success": False, "error": _("Title is required")}, status=400
        )

    subtask = SubtaskService.create_subtask(task, title, description)
    return JsonResponse({"success": True, "subtask": SubtaskService.subtask_to_dict(subtask)})


@login_required
def subtask_update(request, subtask_id):
    """Update a subtask (AJAX)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": _("Invalid method")}, status=405)

    subtask = SubtaskService.get_subtask_by_id(subtask_id, request.user)
    if not subtask:
        return JsonResponse(
            {"success": False, "error": _("Subtask not found")}, status=404
        )

    data = json.loads(request.body)
    SubtaskService.update_subtask(
        subtask,
        title=data.get("title"),
        description=data.get("description"),
        status=data.get("status"),
        order=data.get("order"),
    )
    return JsonResponse({"success": True, "subtask": SubtaskService.subtask_to_dict(subtask)})


@login_required
def subtask_delete(request, subtask_id):
    """Delete a subtask (AJAX)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": _("Invalid method")}, status=405)

    subtask = SubtaskService.get_subtask_by_id(subtask_id, request.user)
    if not subtask:
        return JsonResponse(
            {"success": False, "error": _("Subtask not found")}, status=404
        )

    SubtaskService.delete_subtask(subtask)
    return JsonResponse({"success": True, "message": _("Subtask deleted successfully")})


@login_required
def subtask_toggle(request, subtask_id):
    """Toggle subtask completion; auto-completes parent when all subtasks are done."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": _("Invalid method")}, status=405)

    subtask = SubtaskService.get_subtask_by_id(subtask_id, request.user)
    if not subtask:
        return JsonResponse(
            {"success": False, "error": _("Subtask not found")}, status=404
        )

    subtask, parent_completed = SubtaskService.toggle_subtask(subtask)

    response_data = {
        "success": True,
        "subtask": SubtaskService.subtask_to_dict(subtask),
        "parent_completed": parent_completed,
    }
    if parent_completed:
        response_data["parent_status"] = "completed"
        response_data["parent_status_display"] = _("Completed")

    return JsonResponse(response_data)


@login_required
def subtask_reorder(request, task_id):
    """Reorder subtasks via drag-and-drop (AJAX)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": _("Invalid method")}, status=405)

    task = get_object_or_404(Task, id=task_id, user=request.user)
    data = json.loads(request.body)
    SubtaskService.reorder_subtasks(task, data.get("orders", []))

    return JsonResponse({"success": True, "message": _("Subtasks reordered successfully")})


@login_required
def download_week_preview(request):
    """Preview page for weekly PDF download."""
    data = PDFService.get_week_tasks(request.user)
    return render(request, "tasks/download/preview_week.html", data)


@login_required
def download_month_preview(request):
    """Preview page for monthly PDF download."""
    data = PDFService.get_month_tasks(request.user)
    return render(request, "tasks/download/preview_month.html", data)


def download_pdf(request):
    """Generate and download a PDF report using WeasyPrint."""
    from weasyprint import HTML  # lazy import — requires GTK3 on Windows

    pdf_type = request.GET.get("type", "week")
    data = PDFService.get_pdf_data(request.user, pdf_type)

    html_string = render_to_string(
        data["template"],
        {
            "tasks": data["tasks"],
            "start": data["start"],
            "end": data["end"],
            "user": request.user,
        },
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{data["filename"]}"'
    )

    HTML(
        string=html_string,
        base_url=request.build_absolute_uri()
    ).write_pdf(response)

    return response