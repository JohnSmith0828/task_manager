# backend/tasks/views.py
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    """タスク一覧取得・作成API"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_completed', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """現在ログイン中のユーザーのタスクのみ取得"""
        return Task.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """メソッドに応じてシリアライザーを切り替え"""
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """タスク作成時にユーザーを自動設定"""
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """タスク詳細取得・更新・削除API"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """現在ログイン中のユーザーのタスクのみ取得"""
        return Task.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """メソッドに応じてシリアライザーを切り替え"""
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_task_completion(request, pk):
    """タスクの完了状態を切り替え"""
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        task.is_completed = not task.is_completed
        task.save()
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    except Task.DoesNotExist:
        return Response(
            {'error': 'タスクが見つかりません。'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    """タスク統計API"""
    user_tasks = Task.objects.filter(user=request.user)
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    
    # 優先度別統計
    priority_stats = {}
    for priority, _ in Task.PRIORITY_CHOICES:
        priority_stats[priority] = user_tasks.filter(priority=priority).count()
    
    # 期限切れタスク
    from django.utils import timezone
    overdue_tasks = user_tasks.filter(
        due_date__lt=timezone.now(),
        is_completed=False
    ).count()
    
    return Response({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'priority_stats': priority_stats,
    })