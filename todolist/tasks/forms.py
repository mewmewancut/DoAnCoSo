"""
Django ModelForms for Task and SubTask models.

Replaces manual ``request.POST.get()`` parsing in views with
validated, reusable form classes.
"""
from django import forms
from .models import Task, SubTask, Tag


class TaskForm(forms.ModelForm):
    """
    ModelForm for creating and editing Tasks.

    Provides server-side validation, automatic label generation,
    and widget customisation matching the existing Bootstrap styling.
    """

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox',
        }),
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'priority', 'status', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': 'Example: Complete quarterly report...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-custom',
                'rows': 4,
                'placeholder': 'Add notes or details for this task...',
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-custom',
                'type': 'datetime-local',
            }, format='%Y-%m-%dT%H:%M'),
            'priority': forms.Select(attrs={
                'class': 'form-select form-control-custom',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select form-control-custom',
            }),
        }
        labels = {
            'title': 'Task Title',
            'description': 'Detailed Description',
            'deadline': 'Deadline',
            'priority': 'Priority',
            'status': 'Status',
            'tags': 'Tags',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow deadline input to accept datetime-local format
        self.fields['deadline'].input_formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ]


class SubTaskForm(forms.ModelForm):
    """
    ModelForm for SubTask creation / editing.
    """

    class Meta:
        model = SubTask
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subtask title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Description (optional)',
            }),
        }
