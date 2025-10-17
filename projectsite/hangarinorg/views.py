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
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Case, When, IntegerField, Value, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce, Cast
from django.shortcuts import redirect


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


def root_redirect(request):
    return redirect('dashboard')

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

        # Build task rows with progress computed from subtasks using annotations to avoid N+1 queries
        tasks_qs = (
            Task.objects
            .annotate(
                total_sub=Count('subtasks', distinct=True),
                completed_sub=Count('subtasks', filter=Q(subtasks__status__iexact='Completed'), distinct=True),
            )
            .annotate(
                # compute percent when there are subtasks: (completed_sub / total_sub) * 100
                progress_calc=Case(
                    When(total_sub__gt=0, then=ExpressionWrapper(100.0 * F('completed_sub') / F('total_sub'), output_field=FloatField())),
                    default=None,
                    output_field=FloatField(),
                ),
                # fallback mapping when no subtasks
                fallback_pct=Case(
                    When(status__iexact='Completed', then=Value(100)),
                    When(status__iexact='In Progress', then=Value(50)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
            .annotate(
                progress_int=Cast(Coalesce(F('progress_calc'), F('fallback_pct')), IntegerField())
            )
        )

        # support chainable ordering via ?order=<col>[,<col2>,...] where each col may be prefixed with - for desc
        # allowed keys: task, category, progress, deadline
        order_param = self.request.GET.get('order', '').strip()
        sort_key = self.request.GET.get('sort', '').strip()  # kept for backward compatibility / arrows
        sort_dir = self.request.GET.get('dir', 'asc')
        allowed_sorts = {
            'task': 'title',
            'category': 'category__category_name',
            'progress': 'progress_int',
            'deadline': 'deadline',
        }

        # Parse the requested order list (either from order= or fallback to sort/dir + secondary)
        order_items = []
        if order_param:
            raw = [p.strip() for p in order_param.split(',') if p.strip()]
            order_items = raw
        else:
            # fallback: build from sort & optional secondary_sort/secondary_dir params (older logic)
            primary = self.request.GET.get('sort', '').strip()
            primary_dir = self.request.GET.get('dir', 'asc')
            secondary = self.request.GET.get('secondary_sort', '').strip()
            secondary_dir = self.request.GET.get('secondary_dir', 'asc')
            if primary:
                prefix = '-' if primary_dir == 'desc' else ''
                order_items.append(prefix + primary)
            if secondary:
                sprefix = '-' if secondary_dir == 'desc' else ''
                order_items.append(sprefix + secondary)

        # convert order_items (keys) into ORM order_by fields, preserving sign
        order_by_fields = []
        for it in order_items:
            if not it:
                continue
            sign = '-' if it.startswith('-') else ''
            key = it.lstrip('-')
            if key in allowed_sorts:
                order_field = sign + allowed_sorts[key]
                order_by_fields.append(order_field)

        if order_by_fields:
            try:
                tasks_qs = tasks_qs.order_by(*order_by_fields)
            except Exception:
                # ignore invalid ordering inputs
                pass

        # expose current ordering for template use
        context['current_sort'] = sort_key or (order_items[0].lstrip('-') if order_items else '')
        context['current_direction'] = sort_dir if sort_key else ( 'desc' if order_items and order_items[0].startswith('-') else 'asc')
        context['current_order_items'] = order_items

        # build header links: clicking a header makes it the primary key and appends existing order items as tiebreakers
        header_links = {}
        for col in allowed_sorts.keys():
            # determine toggle direction for this column
            cur_primary = order_items[0].lstrip('-') if order_items else ''
            cur_primary_dir = 'desc' if order_items and order_items[0].startswith('-') else 'asc'
            # if clicking the same primary, toggle; otherwise default to asc
            if cur_primary == col:
                new_dir = 'desc' if cur_primary_dir == 'asc' else 'asc'
            else:
                new_dir = 'asc'
            new_item = ('' if new_dir == 'asc' else '-') + col
            # build new order list with new primary followed by existing items that are not the same column
            new_order = [new_item] + [it for it in order_items if it.lstrip('-') != col]
            header_links[col] = '?order=' + ','.join(new_order)

        context['header_links'] = header_links
        # expose the primary ordering column and direction for template arrow rendering
        if order_items:
            primary = order_items[0]
            context['primary_col'] = primary.lstrip('-')
            context['primary_dir'] = 'desc' if primary.startswith('-') else 'asc'
        else:
            context['primary_col'] = ''
            context['primary_dir'] = 'asc'

        # Build list expected by template: [{'task': TaskInstance, 'progress': int}, ...]
        task_rows = [{'task': t, 'progress': getattr(t, 'progress_int', 0)} for t in tasks_qs]
        context['task_rows'] = task_rows
        
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
    def get_success_url(self):
        return self.request.path
    
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
    def get_success_url(self):
        return self.request.path
    
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
    success_url = reverse_lazy('dashboard')
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
    def get_success_url(self):
        return self.request.path
    
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
    # success URL will send user to the category page after creating a task
    def get_success_url(self):
        # redirect back to the category tasks view for the created task
        try:
            # Note is linked to a Task which belongs to a Category
            return reverse('category_tasks', args=[self.object.task.category.pk])
        except Exception:
            return reverse_lazy('dashboard')
        return self.request.path
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Note'
        context['form_description'] = 'Add a note to a task'
        context['submit_text'] = 'Add Note'
        return context

    def get_initial(self):
        initial = super().get_initial()
        # allow prefilling category via ?category=<pk>
        category_pk = self.request.GET.get('category')
        if category_pk:
            try:
                initial['category'] = int(category_pk)
            except (ValueError, TypeError):
                pass
        return initial


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


class NoteListView(ListView):
    """List all notes, with optional filtering by task via ?task=<task_pk> and search via ?q="""
    model = Note
    template_name = 'notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        qs = Note.objects.select_related('task')
        # optional filter by task
        task_pk = self.request.GET.get('task')
        if task_pk:
            try:
                task_pk = int(task_pk)
                qs = qs.filter(task__pk=task_pk)
            except (ValueError, TypeError):
                pass

        # search across note content and related task title
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(content__icontains=q) |
                Q(task__title__icontains=q)
            )

        # support simple ordering via ?sort=created_at|task and dir=asc|desc
        sort_key = self.request.GET.get('sort', '').strip()
        sort_dir = self.request.GET.get('dir', 'asc')
        allowed = {
            'created_at': 'created_at',
            'task': 'task__title',
        }
        if sort_key in allowed:
            field = allowed[sort_key]
            if sort_dir == 'desc':
                field = '-' + field
            try:
                qs = qs.order_by(field)
            except Exception:
                pass

        # default ordering newest first
        if not self.request.GET.get('sort'):
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_direction'] = self.request.GET.get('dir', 'asc')
        context.update({
            'category_name': 'Notes',
            'category_color': 'info',
            'category_pk': None,
            'labels': {
                'add_task': 'Add Note',
                'create_first': 'Create Your First Note',
                'task_col': 'Note',
                'priority_col': 'Task',
                'status_col': 'Created',
                'due_col': 'Created At',
            }
        })
        return context


# ========== SUBTASK CRUD VIEWS ==========

class SubTaskCreateView(CreateView):
    """View for creating new subtasks"""
    model = SubTask
    form_class = SubTaskForm
    template_name = 'subtask_form.html'
    def get_success_url(self):
        return self.request.path
    
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


class SubTaskListView(ListView):
    """List all subtasks, with optional filtering by parent task via ?parent=<task_pk>."""
    model = SubTask
    template_name = 'subtasks.html'
    context_object_name = 'subtasks'

    def get_queryset(self):
        # SubTask doesn't have its own priority/deadline; use parent task's relations
        qs = SubTask.objects.select_related('parent_task', 'parent_task__priority')
        parent = self.request.GET.get('parent')
        if parent:
            try:
                parent_pk = int(parent)
                qs = qs.filter(parent_task__pk=parent_pk)
            except (ValueError, TypeError):
                pass
        # support filtering by parent task priority via query param ?priority=<pk>
        priority = self.request.GET.get('priority')
        if priority:
            try:
                priority_pk = int(priority)
                qs = qs.filter(parent_task__priority__pk=priority_pk)
            except (ValueError, TypeError):
                pass

        # support filtering by subtask status via ?status=Completed|In Progress|Pending
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status__iexact=status)

        # optional search across subtask title/description
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )

        # support sorting via ?sort=<key>&dir=asc|desc (same semantic sorts as tasks)
        sort_key = self.request.GET.get('sort', '').strip()
        sort_dir = self.request.GET.get('dir', 'asc')

        if sort_key == 'priority':
            priority_order_case = Case(
                When(parent_task__priority__priority_name__iexact='critical', then=Value(1)),
                When(parent_task__priority__priority_name__iexact='high', then=Value(2)),
                When(parent_task__priority__priority_name__iexact='medium', then=Value(3)),
                When(parent_task__priority__priority_name__iexact='low', then=Value(4)),
                When(parent_task__priority__priority_name__iexact='optional', then=Value(5)),
                default=Value(999),
                output_field=IntegerField(),
            )
            try:
                qs = qs.annotate(priority_rank=priority_order_case)
                if sort_dir == 'desc':
                    qs = qs.order_by('-priority_rank')
                else:
                    qs = qs.order_by('priority_rank')
            except Exception:
                pass
        else:
            allowed_sorts = {
                'title': 'title',
                'task': 'title',
                'status': 'status',
                'deadline': 'parent_task__deadline',
                'due': 'parent_task__deadline',
            }
            if sort_key in allowed_sorts:
                order_field = allowed_sorts[sort_key]
                if sort_dir == 'desc':
                    order_field = '-' + order_field
                try:
                    qs = qs.order_by(order_field)
                except Exception:
                    pass

        # default fallback ordering
        if not self.request.GET.get('sort'):
            qs = qs.order_by('-updated_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['priorities'] = Priority.objects.all()
        context['selected_priority'] = self.request.GET.get('priority', '')
        context.update({
            'category_name': 'Subtasks',
            'category_color': 'primary',
            'category_pk': None,
            'labels': {
                'add_task': 'Add Subtask',
                'create_first': 'Create Your First Subtask',
                'task_col': 'Subtask',
                'priority_col': 'Priority',
                'status_col': 'Status',
                'due_col': 'Due Date',
            }
        })
        # expose sorting state for the template (so arrows and links work)
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_direction'] = self.request.GET.get('dir', 'asc')

        context['search_query'] = self.request.GET.get('q', '')
        return context


 


from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone

class CategoryTasksView(ListView):
    """Displays all tasks under a given category (dynamic by pk)."""
    model = Task
    template_name = 'category_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        category_pk = self.kwargs.get('pk')
        qs = Task.objects.filter(category__pk=category_pk)

        # support filtering by priority via query param ?priority=<pk>
        priority = self.request.GET.get('priority')
        if priority:
            try:
                priority_pk = int(priority)
                qs = qs.filter(priority__pk=priority_pk)
            except (ValueError, TypeError):
                pass

        # support filtering by status via ?status=Completed|In Progress|Pending
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status__iexact=status)

        # 🔍 NEW: support search via ?q=keyword
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # support sorting via ?sort=<key>&dir=asc|desc
        sort_key = self.request.GET.get('sort', '').strip()
        sort_dir = self.request.GET.get('dir', 'asc')

        # Special-case: semantic ordering for priority names instead of alphabetical
        if sort_key == 'priority':
            priority_order_case = Case(
                When(priority__priority_name__iexact='critical', then=Value(1)),
                When(priority__priority_name__iexact='high', then=Value(2)),
                When(priority__priority_name__iexact='medium', then=Value(3)),
                When(priority__priority_name__iexact='low', then=Value(4)),
                When(priority__priority_name__iexact='optional', then=Value(5)),
                default=Value(999),
                output_field=IntegerField(),
            )
            try:
                qs = qs.annotate(priority_rank=priority_order_case)
                if sort_dir == 'desc':
                    qs = qs.order_by('-priority_rank')
                else:
                    qs = qs.order_by('priority_rank')
            except Exception:
                pass
        else:
            allowed_sorts = {
                'title': 'title',
                'task': 'title',
                'status': 'status',
                'deadline': 'deadline',
                'due': 'deadline',
            }
            if sort_key in allowed_sorts:
                order_field = allowed_sorts[sort_key]
                if sort_dir == 'desc':
                    order_field = '-' + order_field
                try:
                    qs = qs.order_by(order_field)
                except Exception:
                    pass

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_pk = self.kwargs.get('pk')
        category = Category.objects.filter(pk=category_pk).first()

        # expose available priorities and the selected priority for the template
        context['priorities'] = Priority.objects.all()
        context['selected_priority'] = self.request.GET.get('priority', '')

        # expose sorting state for the template
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_direction'] = self.request.GET.get('dir', 'asc')

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
        overdue = qs.exclude(deadline__isnull=True).filter(deadline__lt=today).exclude(status__iexact='Completed').count()

        context.update({
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'in_progress_tasks': in_progress,
            'overdue_tasks': overdue,
        })

        # Expose editable UI text labels so copy can be changed centrally
        context['labels'] = {
            'add_task': 'Add Task',
            'create_first': 'Create Your First Task',
            'task_col': 'Task',
            'priority_col': 'Priority',
            'status_col': 'Status',
            'due_col': 'Due Date',
        }

        # 🔍 include current search query back to template for form value
        context['search_query'] = self.request.GET.get('q', '')

        return context


        
