from django import forms
from django.forms import ModelForm, DateTimeInput
from .models import Task, Category, Priority, Note, SubTask


class TaskForm(ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'category', 'priority', 'status']

        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }


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






