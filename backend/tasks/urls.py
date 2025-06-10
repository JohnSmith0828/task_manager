# backend/tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/toggle/', views.toggle_task_completion, name='task-toggle'),
    path('statistics/', views.task_statistics, name='task-statistics'),
]