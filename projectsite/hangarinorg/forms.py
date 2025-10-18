from django import forms
from django.forms import ModelForm, DateTimeInput
from django.core.exceptions import ValidationError
from .models import Task, Category, Priority, Note, SubTask


class TaskForm(ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'category', 'priority', 'status']

        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    # Constrain year range in the browser UI; browsers that honor this will prevent invalid years
                    "min": "1900-01-01T00:00",
                    "max": "2100-12-31T23:59",
                }
            ),
            "description": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        # If parsing failed, Django will raise before this; if present, validate year bounds
        if deadline is None:
            return deadline
        year = getattr(deadline, 'year', None)
        if year is None:
            return deadline
        # Enforce a sensible 4-digit year range to avoid accidental 5-6 digit years
        if year < 1900 or year > 2100:
            raise ValidationError("Please enter a year between 1900 and 2100 for the deadline.")
        return deadline


class CategoryForm(ModelForm):
    """Form for managing categories"""
    
    class Meta:
        model = Category
        fields = ['category_name']


class PriorityForm(ModelForm):
    """Form for managing priorities"""
    
    class Meta:
        model = Priority
        fields = ['priority_name']


class NoteForm(ModelForm):
    """Form for adding notes to tasks"""
    
    class Meta:
        model = Note
        fields = ['task', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }


class SubTaskForm(ModelForm):
    """Form for creating subtasks"""
    
    class Meta:
        model = SubTask
        fields = ['parent_task', 'title', 'status']






