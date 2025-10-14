import os
import subprocess
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from hangarinorg.models import Task, Category, Priority, Note, SubTask
from hangarinorg.forms import TaskForm, CategoryForm, PriorityForm, NoteForm, SubTaskForm
from django.urls import reverse_lazy
from django.utils import timezone


logger = logging.getLogger(__name__)

@csrf_exempt  # allows external POST requests (like from GitHub)
@require_POST  # only allow POST requests, reject GET
def deploy(request):
    auth = request.headers.get("Authorization", "")
    expected = f"Bearer {os.environ.get('DEPLOY_TOKEN', '')}"
    if auth != expected:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # If authorized, proceed with deployment
    manage_dir = "/home/rosevent/hangarin/projectsite"  # directory where manage.py is located
    project_dir = "/home/rosevent/hangarin"  # where .git is
    wsgi_path = "/var/www/rosevent_pythonanywhere_com_wsgi.py"
    venv_path = "/home/rosevent/Hangarinenv/bin"

    try:
        # 1. Fetch latest version
        subprocess.run(["git", "fetch"], cwd=project_dir, check=True)
        diff = subprocess.run(
            ["git", "diff", "--name-only", "origin/main"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True
        ).stdout

        # 2. Pull updates
        subprocess.run(["git", "pull", "origin", "main"], cwd=project_dir, check=True)
        logger.info("Pulled latest code from GitHub.")

        # 3. Install dependencies
        subprocess.run(
            [f"{venv_path}/pip", "install", "-r", "requirements.txt"],
            cwd=project_dir,
            check=True
        )
        logger.info("Dependencies installed.")

        # 4. Run migrations only if new ones detected
        if "migrations/" in diff:
            logger.info("New migration files detected. Running migrate...")
            subprocess.run(
                [f"{venv_path}/python", "manage.py", "migrate"],
                cwd=manage_dir,
                check=True
            )
        else:
            logger.info("No new migrations detected. Skipping migrate...")

        # 5. Reload web app
        subprocess.run(["touch", wsgi_path], check=True)
        logger.info("Web app reloaded.")

    except subprocess.CalledProcessError as e:
        logger.exception("Command failed")
        return JsonResponse({"error": "Command failed", "details": str(e)}, status=500)

    except Exception as e:
        logger.exception("Deployment failed")
        return JsonResponse({"error": "Deployment failed", "details": str(e)}, status=500)

    return JsonResponse({"status": "Deployed successfully"})


class HomePageView(ListView):
    model = Task
    template_name = 'dashboard.html'
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
        
        # Add tasks grouped by category dynamically (no hardcoded category names)
        category_groups = []
        for cat in Category.objects.all():
            qs = all_tasks.filter(category=cat)
            category_groups.append({'category': cat, 'tasks': qs})
        context['category_task_groups'] = category_groups
        
        return context

class TaskListView(ListView):
    model = Task
    template_name = 'dashboard.html'
    context_object_name = 'tasks'



# Category-specific views



# ========== TASK CRUD VIEWS ==========

class TaskDetailView(DetailView):
    """View for displaying a single task with details"""
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'


class TaskCreateView(CreateView):
    """View for creating new tasks"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Task'
        context['form_description'] = 'Fill in the details to create a new task'
        context['submit_text'] = 'Create Task'
        return context


class TaskUpdateView(UpdateView):
    """View for updating existing tasks"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Task: {self.object.title}'
        context['form_description'] = 'Update the task details below'
        context['submit_text'] = 'Update Task'
        return context


class TaskDeleteView(DeleteView):
    """View for deleting tasks"""
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'task'


# ========== CATEGORY CRUD VIEWS ==========

class CategoryListView(ListView):
    """View for listing all categories"""
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    """View for displaying a single category with its tasks"""
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects.filter(category=self.object)
        return context


class CategoryCreateView(CreateView):
    """View for creating new categories"""
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Category'
        context['form_description'] = 'Add a new task category'
        context['submit_text'] = 'Create Category'
        return context


class CategoryUpdateView(UpdateView):
    """View for updating existing categories"""
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Category: {self.object.category_name}'
        context['form_description'] = 'Update the category details'
        context['submit_text'] = 'Update Category'
        return context


class CategoryDeleteView(DeleteView):
    """View for deleting categories"""
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    context_object_name = 'category'


# ========== PRIORITY CRUD VIEWS ==========

class PriorityListView(ListView):
    """View for listing all priorities"""
    model = Priority
    template_name = 'priority_list.html'
    context_object_name = 'priorities'


class PriorityCreateView(CreateView):
    """View for creating new priorities"""
    model = Priority
    form_class = PriorityForm
    template_name = 'priority_form.html'
    success_url = reverse_lazy('priority_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Priority'
        context['form_description'] = 'Add a new priority level'
        context['submit_text'] = 'Create Priority'
        return context


class PriorityUpdateView(UpdateView):
    """View for updating existing priorities"""
    model = Priority
    form_class = PriorityForm
    template_name = 'priority_form.html'
    success_url = reverse_lazy('priority_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Priority: {self.object.priority_name}'
        context['form_description'] = 'Update the priority details'
        context['submit_text'] = 'Update Priority'
        return context


class PriorityDeleteView(DeleteView):
    """View for deleting priorities"""
    model = Priority
    template_name = 'priority_confirm_delete.html'
    success_url = reverse_lazy('priority_list')
    context_object_name = 'priority'


# ========== NOTE CRUD VIEWS ==========

class NoteCreateView(CreateView):
    """View for creating new notes"""
    model = Note
    form_class = NoteForm
    template_name = 'note_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Note'
        context['form_description'] = 'Add a note to a task'
        context['submit_text'] = 'Add Note'
        return context


class NoteUpdateView(UpdateView):
    """View for updating existing notes"""
    model = Note
    form_class = NoteForm
    template_name = 'note_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Note'
        context['form_description'] = 'Update the note content'
        context['submit_text'] = 'Update Note'
        return context


class NoteDeleteView(DeleteView):
    """View for deleting notes"""
    model = Note
    template_name = 'note_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'note'


# ========== SUBTASK CRUD VIEWS ==========

class SubTaskCreateView(CreateView):
    """View for creating new subtasks"""
    model = SubTask
    form_class = SubTaskForm
    template_name = 'subtask_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Subtask'
        context['form_description'] = 'Add a subtask to a main task'
        context['submit_text'] = 'Create Subtask'
        return context


class SubTaskUpdateView(UpdateView):
    """View for updating existing subtasks"""
    model = SubTask
    form_class = SubTaskForm
    template_name = 'subtask_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Subtask: {self.object.title}'
        context['form_description'] = 'Update the subtask details'
        context['submit_text'] = 'Update Subtask'
        return context


class SubTaskDeleteView(DeleteView):
    """View for deleting subtasks"""
    model = SubTask
    template_name = 'subtask_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'subtask'


 


class CategoryTasksView(ListView):
    """Displays all tasks under a given category (dynamic by pk)."""
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        category_pk = self.kwargs.get('pk')
        return Task.objects.filter(category__pk=category_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_pk = self.kwargs.get('pk')
        category = Category.objects.filter(pk=category_pk).first()
        # base category info
        context.update({
            'category_name': category.category_name if category else 'Category',
            'category_icon': getattr(category, 'icon', 'mdi-folder-outline') if category else 'mdi-folder-outline',
            'category_color': getattr(category, 'color', 'secondary') if category else 'secondary',
            'category_pk': category_pk,
        })

        # compute category-specific task statistics for dashboard cards
        qs = Task.objects.filter(category=category) if category else Task.objects.none()
        today = timezone.now().date()
        total = qs.count()
        completed = qs.filter(status__iexact='Completed').count()
        pending = qs.filter(status__iexact='Pending').count()
        in_progress = qs.filter(status__iexact='In Progress').count()

        # Use 'deadline' field (exists on Task). Support both DateField and DateTimeField.
        # Filter tasks with a non-null deadline less than today and not completed.
        overdue = qs.exclude(deadline__isnull=True).filter(deadline__lt=today).exclude(status__iexact='Completed').count()

        context.update({
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'in_progress_tasks': in_progress,
            'overdue_tasks': overdue,
        })
        return context
