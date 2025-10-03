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
from hangarinorg.views import HomePageView, TaskListView
from hangarinorg import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomePageView.as_view(), name='base'),
    
    # Category-specific task URLs
    path('tasks/personal/', views.PersonalTasksView.as_view(), name='personal_tasks'),
    path('tasks/projects/', views.ProjectTasksView.as_view(), name='project_tasks'),
    path('tasks/school/', views.SchoolTasksView.as_view(), name='school_tasks'),
    path('tasks/work/', views.WorkTasksView.as_view(), name='work_tasks'),
    path('tasks/finance/', views.FinanceTasksView.as_view(), name='finance_tasks'),
]
