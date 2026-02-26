import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """
    Tag model for categorising tasks.
    """
    COLOR_CHOICES = [
        ('#c3392b', 'Red'),
        ('#2ecc71', 'Green'),
        ('#3498db', 'Blue'),
        ('#f39c12', 'Orange'),
        ('#9b59b6', 'Purple'),
        ('#1abc9c', 'Teal'),
        ('#e74c3c', 'Crimson'),
        ('#34495e', 'Dark'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#3498db')

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Task(models.Model):
    """
    Task model for TodoList application
    """
    # Priority choices
    PRIORITY_CHOICES = [
    ('low', _('Low')),
    ('medium', _('Medium')),
    ('high', _('High')),
]
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
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
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
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
        ('coach', 'Productivity Coaching'),
        ('search', 'Smart Search'),
        ('tags', 'Auto Tagging'),
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


class SubTask(models.Model):
    """
    SubTask model for breaking down tasks into smaller actionable items
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='subtasks'
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    order = models.IntegerField(default=0)  # For drag & drop ordering
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'SubTask'
        verbose_name_plural = 'SubTasks'
    
    def __str__(self):
        return f"{self.task.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Override save to track completion time"""
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed' and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        """Check if subtask is completed"""
        return self.status == 'completed'
