from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from hangarinorg.models import Task, Category, Priority

# Create your views here.

class HomePageView(ListView):
    model = Task
    template_name = 'base.html'
    context_object_name = 'tasks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add categories and priorities for filtering/display
        context['categories'] = Category.objects.all()
        context['priorities'] = Priority.objects.all()
        
        # Add task statistics
        all_tasks = Task.objects.all()
        context['total_tasks'] = all_tasks.count()
        context['completed_tasks'] = all_tasks.filter(status='Completed').count()
        context['pending_tasks'] = all_tasks.filter(status='Pending').count()
        context['in_progress_tasks'] = all_tasks.filter(status='In Progress').count()
        
        # Add tasks by category
        context['personal_tasks'] = all_tasks.filter(category__category_name='Personal')
        context['project_tasks'] = all_tasks.filter(category__category_name='Projects')
        context['school_tasks'] = all_tasks.filter(category__category_name='School')
        context['work_tasks'] = all_tasks.filter(category__category_name='Work')
        context['finance_tasks'] = all_tasks.filter(category__category_name='Finance')
        
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
        
        # Add categories and priorities for filtering/display
        context['categories'] = Category.objects.all()
        context['priorities'] = Priority.objects.all()
        
        # Add statistics for the todo list
        all_tasks = Task.objects.all()
        context['total_tasks'] = all_tasks.count()
        context['completed_tasks'] = all_tasks.filter(status='Completed').count()
        context['pending_tasks'] = all_tasks.filter(status='Pending').count()
        context['in_progress_tasks'] = all_tasks.filter(status='In Progress').count()
        
        # Add tasks by category for filtering
        context['personal_tasks'] = all_tasks.filter(category__category_name='Personal')
        context['project_tasks'] = all_tasks.filter(category__category_name='Projects')
        context['school_tasks'] = all_tasks.filter(category__category_name='School')
        context['work_tasks'] = all_tasks.filter(category__category_name='Work')
        context['finance_tasks'] = all_tasks.filter(category__category_name='Finance')
        
        # Add tasks by priority
        context['optional_priority_tasks'] = all_tasks.filter(priority__priority_name='Optional')
        context['low_priority_tasks'] = all_tasks.filter(priority__priority_name='Low')
        context['medium_priority_tasks'] = all_tasks.filter(priority__priority_name='Medium')
        context['high_priority_tasks'] = all_tasks.filter(priority__priority_name='High')
        context['critical_priority_tasks'] = all_tasks.filter(priority__priority_name='Critical')
        
        return context

# Category-specific views
class PersonalTasksView(ListView):
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Personal')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = 'Personal'
        context['category_icon'] = 'mdi-account'
        context['category_color'] = 'primary'
        return context

class ProjectTasksView(ListView):
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Projects')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = 'Projects'
        context['category_icon'] = 'mdi-briefcase'
        context['category_color'] = 'success'
        return context

class SchoolTasksView(ListView):
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='School')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = 'School'
        context['category_icon'] = 'mdi-school'
        context['category_color'] = 'info'
        return context

class WorkTasksView(ListView):
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Work')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = 'Work'
        context['category_icon'] = 'mdi-office-building'
        context['category_color'] = 'warning'
        return context

class FinanceTasksView(ListView):
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Finance')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = 'Finance'
        context['category_icon'] = 'mdi-cash'
        context['category_color'] = 'danger'
        return context
