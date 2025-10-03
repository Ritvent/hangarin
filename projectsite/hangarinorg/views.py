from django.shortcuts import render
from django.views.generic.list import ListView
from hangarinorg.models import Task 

# Create your views here.

class HomePageView(ListView):
    model = Task
    template_name = 'base.html'
    context_object_name = 'tasks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add extra context if needed (categories, priorities, etc.)
        return context

class TaskListView(ListView):
    model = Task
    template_name = 'base.html'
    context_object_name = 'tasks'

class TodoListView(ListView):
    model = Task
    template_name = 'todo_list.html'
    context_object_name = 'tasks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics for the todo list
        all_tasks = Task.objects.all()
        context['total_tasks'] = all_tasks.count()
        context['completed_tasks'] = all_tasks.filter(status='completed').count()
        context['pending_tasks'] = all_tasks.filter(status='pending').count()
        context['in_progress_tasks'] = all_tasks.filter(status='in_progress').count()
        return context
