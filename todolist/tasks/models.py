import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    """
    Task model for TodoList application
    """
    # Priority choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Override save to track completion time"""
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed' and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and self.status != 'completed':
            return timezone.now() > self.deadline
        return False
    
    @property
    def completion_time(self):
        """Calculate time taken to complete the task"""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def days_to_deadline(self):
        """Calculate days remaining to deadline"""
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None


class AISuggestion(models.Model):
    """
    Model to track AI suggestions history for tasks
    """
    SUGGESTION_TYPES = [
        ('description', 'Description Improvement'),
        ('priority', 'Priority Suggestion'),
        ('subtasks', 'Subtasks Generation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='ai_suggestions',
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    input_data = models.JSONField()  # Store the input sent to AI
    output_data = models.JSONField()  # Store the AI response
    applied = models.BooleanField(default=False)  # Whether user applied the suggestion
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Suggestion'
        verbose_name_plural = 'AI Suggestions'
    
    def __str__(self):
        return f"{self.get_suggestion_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
