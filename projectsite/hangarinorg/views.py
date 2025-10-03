from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from hangarinorg.models import Task, Category, Priority, Note, SubTask
from hangarinorg.forms import TaskForm, CategoryForm, PriorityForm, NoteForm, SubTaskForm
from django.urls import reverse_lazy

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
    success_url = reverse_lazy('base')
    
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
    success_url = reverse_lazy('base')
    
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
    success_url = reverse_lazy('base')
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
    success_url = reverse_lazy('base')
    
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
    success_url = reverse_lazy('base')
    
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
    success_url = reverse_lazy('base')
    context_object_name = 'note'


# ========== SUBTASK CRUD VIEWS ==========

class SubTaskCreateView(CreateView):
    """View for creating new subtasks"""
    model = SubTask
    form_class = SubTaskForm
    template_name = 'subtask_form.html'
    success_url = reverse_lazy('base')
    
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
    success_url = reverse_lazy('base')
    
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
    success_url = reverse_lazy('base')
    context_object_name = 'subtask'


# ========== CATEGORY-SPECIFIC CRUD VIEWS ==========

# Personal Task Views
class PersonalTaskCreateView(CreateView):
    """Create personal tasks with category pre-set"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('personal_tasks')
    
    def form_valid(self, form):
        form.instance.category = Category.objects.get(category_name='Personal')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Personal Task'
        context['form_description'] = 'Add a new personal task'
        context['submit_text'] = 'Create Task'
        return context


class PersonalTaskDetailView(DetailView):
    """View personal task details with category validation"""
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Personal')


class PersonalTaskUpdateView(UpdateView):
    """Edit personal tasks with category validation"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('personal_tasks')
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Personal')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Personal Task: {self.object.title}'
        context['form_description'] = 'Update your personal task'
        context['submit_text'] = 'Update Task'
        return context


class PersonalTaskDeleteView(DeleteView):
    """Delete personal tasks with category validation"""
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('personal_tasks')
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Personal')


# Project Task Views
class ProjectTaskCreateView(CreateView):
    """Create project tasks with category pre-set"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('project_tasks')
    
    def form_valid(self, form):
        form.instance.category = Category.objects.get(category_name='Projects')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Project Task'
        context['form_description'] = 'Add a new project task'
        context['submit_text'] = 'Create Task'
        return context


class ProjectTaskDetailView(DetailView):
    """View project task details with category validation"""
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Projects')


class ProjectTaskUpdateView(UpdateView):
    """Edit project tasks with category validation"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('project_tasks')
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Projects')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Project Task: {self.object.title}'
        context['form_description'] = 'Update your project task'
        context['submit_text'] = 'Update Task'
        return context


class ProjectTaskDeleteView(DeleteView):
    """Delete project tasks with category validation"""
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('project_tasks')
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Projects')


# School Task Views
class SchoolTaskCreateView(CreateView):
    """Create school tasks with category pre-set"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('school_tasks')
    
    def form_valid(self, form):
        form.instance.category = Category.objects.get(category_name='School')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create School Task'
        context['form_description'] = 'Add a new school task'
        context['submit_text'] = 'Create Task'
        return context


class SchoolTaskDetailView(DetailView):
    """View school task details with category validation"""
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='School')


class SchoolTaskUpdateView(UpdateView):
    """Edit school tasks with category validation"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('school_tasks')
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='School')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit School Task: {self.object.title}'
        context['form_description'] = 'Update your school task'
        context['submit_text'] = 'Update Task'
        return context


class SchoolTaskDeleteView(DeleteView):
    """Delete school tasks with category validation"""
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('school_tasks')
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='School')


# Work Task Views
class WorkTaskCreateView(CreateView):
    """Create work tasks with category pre-set"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('work_tasks')
    
    def form_valid(self, form):
        form.instance.category = Category.objects.get(category_name='Work')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Work Task'
        context['form_description'] = 'Add a new work task'
        context['submit_text'] = 'Create Task'
        return context


class WorkTaskDetailView(DetailView):
    """View work task details with category validation"""
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Work')


class WorkTaskUpdateView(UpdateView):
    """Edit work tasks with category validation"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('work_tasks')
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Work')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Work Task: {self.object.title}'
        context['form_description'] = 'Update your work task'
        context['submit_text'] = 'Update Task'
        return context


class WorkTaskDeleteView(DeleteView):
    """Delete work tasks with category validation"""
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('work_tasks')
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Work')


# Finance Task Views
class FinanceTaskCreateView(CreateView):
    """Create finance tasks with category pre-set"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('finance_tasks')
    
    def form_valid(self, form):
        form.instance.category = Category.objects.get(category_name='Finance')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Finance Task'
        context['form_description'] = 'Add a new finance task'
        context['submit_text'] = 'Create Task'
        return context


class FinanceTaskDetailView(DetailView):
    """View finance task details with category validation"""
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Finance')


class FinanceTaskUpdateView(UpdateView):
    """Edit finance tasks with category validation"""
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('finance_tasks')
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Finance')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Finance Task: {self.object.title}'
        context['form_description'] = 'Update your finance task'
        context['submit_text'] = 'Update Task'
        return context


class FinanceTaskDeleteView(DeleteView):
    """Delete finance tasks with category validation"""
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('finance_tasks')
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(category__category_name='Finance')


# ========== EXISTING CATEGORY-SPECIFIC VIEWS ==========

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
