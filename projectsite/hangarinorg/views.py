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
