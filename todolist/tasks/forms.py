"""Django ModelForm for the Task model."""

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Tag, Task


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
        self.fields["deadline"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]

    def clean_deadline(self):
        """Reject deadlines that are in the past (new tasks only)."""
        deadline = self.cleaned_data.get("deadline")
        is_new = self.instance._state.adding
        if deadline and is_new and deadline < timezone.now():
            raise forms.ValidationError(
                _("The deadline cannot be in the past."),
                code="deadline_in_past",
            )
        return deadline
