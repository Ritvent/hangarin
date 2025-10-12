"""
URL configuration for projectsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hangarinorg.views import deploy
from hangarinorg.views import HomePageView, TaskListView
from hangarinorg import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomePageView.as_view(), name='base'),
    path("deploy/", views.deploy, name="deploy"),
    
    # ========== GENERAL TASK URLS ==========
    path('task/', views.TaskListView.as_view(), name='task_list'),
    path('task/create/', views.TaskCreateView.as_view(), name='task_create'),
    
    # ========== PERSONAL TASK URLS ==========
    path('task/personal/', views.PersonalTasksView.as_view(), name='personal_tasks'),
    path('task/personal/create/', views.PersonalTaskCreateView.as_view(), name='personal_task_create'),
    path('task/personal/<int:pk>/', views.PersonalTaskDetailView.as_view(), name='personal_task_detail'),
    path('task/personal/<int:pk>/edit/', views.PersonalTaskUpdateView.as_view(), name='personal_task_edit'),
    path('task/personal/<int:pk>/delete/', views.PersonalTaskDeleteView.as_view(), name='personal_task_delete'),
    
    # ========== PROJECT TASK URLS ==========
    path('task/projects/', views.ProjectTasksView.as_view(), name='project_tasks'),
    path('task/projects/create/', views.ProjectTaskCreateView.as_view(), name='project_task_create'),
    path('task/projects/<int:pk>/', views.ProjectTaskDetailView.as_view(), name='project_task_detail'),
    path('task/projects/<int:pk>/edit/', views.ProjectTaskUpdateView.as_view(), name='project_task_edit'),
    path('task/projects/<int:pk>/delete/', views.ProjectTaskDeleteView.as_view(), name='project_task_delete'),
    
    # ========== SCHOOL TASK URLS ==========
    path('task/school/', views.SchoolTasksView.as_view(), name='school_tasks'),
    path('task/school/create/', views.SchoolTaskCreateView.as_view(), name='school_task_create'),
    path('task/school/<int:pk>/', views.SchoolTaskDetailView.as_view(), name='school_task_detail'),
    path('task/school/<int:pk>/edit/', views.SchoolTaskUpdateView.as_view(), name='school_task_edit'),
    path('task/school/<int:pk>/delete/', views.SchoolTaskDeleteView.as_view(), name='school_task_delete'),
    
    # ========== WORK TASK URLS ==========
    path('task/work/', views.WorkTasksView.as_view(), name='work_tasks'),
    path('task/work/create/', views.WorkTaskCreateView.as_view(), name='work_task_create'),
    path('task/work/<int:pk>/', views.WorkTaskDetailView.as_view(), name='work_task_detail'),
    path('task/work/<int:pk>/edit/', views.WorkTaskUpdateView.as_view(), name='work_task_edit'),
    path('task/work/<int:pk>/delete/', views.WorkTaskDeleteView.as_view(), name='work_task_delete'),
    
    # ========== FINANCE TASK URLS ==========
    path('task/finance/', views.FinanceTasksView.as_view(), name='finance_tasks'),
    path('task/finance/create/', views.FinanceTaskCreateView.as_view(), name='finance_task_create'),
    path('task/finance/<int:pk>/', views.FinanceTaskDetailView.as_view(), name='finance_task_detail'),
    path('task/finance/<int:pk>/edit/', views.FinanceTaskUpdateView.as_view(), name='finance_task_edit'),
    path('task/finance/<int:pk>/delete/', views.FinanceTaskDeleteView.as_view(), name='finance_task_delete'),
    
    # ========== CATEGORY CRUD URLs ==========
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # ========== PRIORITY CRUD URLs ==========
    path('priorities/', views.PriorityListView.as_view(), name='priority_list'),
    path('priority/create/', views.PriorityCreateView.as_view(), name='priority_create'),
    path('priority/<int:pk>/edit/', views.PriorityUpdateView.as_view(), name='priority_edit'),
    path('priority/<int:pk>/delete/', views.PriorityDeleteView.as_view(), name='priority_delete'),
    
    # ========== NOTE CRUD URLs ==========
    path('note/create/', views.NoteCreateView.as_view(), name='note_create'),
    path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('note/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    
    # ========== SUBTASK CRUD URLs ==========
    path('subtask/create/', views.SubTaskCreateView.as_view(), name='subtask_create'),
    path('subtask/<int:pk>/edit/', views.SubTaskUpdateView.as_view(), name='subtask_edit'),
    path('subtask/<int:pk>/delete/', views.SubTaskDeleteView.as_view(), name='subtask_delete'),
]
