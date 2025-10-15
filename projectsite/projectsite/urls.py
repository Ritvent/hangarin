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
from django.urls import path, include
from hangarinorg.views import deploy, root_redirect
from hangarinorg.views import HomePageView, TaskListView
from hangarinorg import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect),
    path('', include('pwa.urls')),
    path('dashboard/', views.HomePageView.as_view(), name='dashboard'),
    path("deploy/", views.deploy, name="deploy"),
    # ========== GENERAL TASK URLS ==========
    path('task/', views.TaskListView.as_view(), name='task_list'),
    path('task/create/', views.TaskCreateView.as_view(), name='task_create'),
    
    
    # ========== GENERAL TASK DETAIL/EDIT/DELETE (generic) ==========
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    # Dynamic category task view (by pk)
    path('task/category/<int:pk>/', views.CategoryTasksView.as_view(), name='category_tasks'),

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
