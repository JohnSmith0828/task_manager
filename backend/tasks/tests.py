# backend/tasks/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Task


class TaskModelTest(TestCase):
    """Taskモデルの単体テスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_task_creation(self):
        """タスク作成テスト"""
        task = Task.objects.create(
            user=self.user,
            title='テストタスク',
            description='テスト用のタスクです'
        )
        self.assertEqual(task.title, 'テストタスク')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.is_completed)
        self.assertEqual(task.priority, 'medium')
    
    def test_task_str_method(self):
        """タスクの文字列表現テスト"""
        task = Task.objects.create(
            user=self.user,
            title='テストタスク'
        )
        expected_str = f"テストタスク - {self.user.username}"
        self.assertEqual(str(task), expected_str)
    
    def test_task_ordering(self):
        """タスクの並び順テスト"""
        task1 = Task.objects.create(user=self.user, title='タスク1')
        task2 = Task.objects.create(user=self.user, title='タスク2')
        
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)  # 最新が最初
        self.assertEqual(tasks[1], task1)


class TaskAPITest(APITestCase):
    """TaskAPI の結合テスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.task_data = {
            'title': 'テストタスク',
            'description': 'テスト用タスク',
            'priority': 'high'
        }
    
    def test_create_task(self):
        """タスク作成APIテスト"""
        url = reverse('task-list-create')
        response = self.client.post(url, self.task_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'テストタスク')
    
    def test_get_task_list(self):
        """タスク一覧取得APIテスト"""
        Task.objects.create(user=self.user, title='タスク1')
        Task.objects.create(user=self.user, title='タスク2')
        
        url = reverse('task-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_update_task(self):
        """タスク更新APIテスト"""
        task = Task.objects.create(user=self.user, title='元のタスク')
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        update_data = {'title': '更新されたタスク', 'is_completed': True}
        response = self.client.put(url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, '更新されたタスク')
        self.assertTrue(task.is_completed)
    
    def test_delete_task(self):
        """タスク削除APIテスト"""
        task = Task.objects.create(user=self.user, title='削除するタスク')
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_toggle_task_completion(self):
        """タスク完了状態切り替えAPIテスト"""
        task = Task.objects.create(user=self.user, title='切り替えタスク')
        
        url = reverse('task-toggle', kwargs={'pk': task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)
    
    def test_unauthorized_access(self):
        """認証なしアクセステスト"""
        self.client.credentials()  # 認証情報をクリア
        url = reverse('task-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_isolation(self):
        """ユーザー間のタスク分離テスト"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        Task.objects.create(user=other_user, title='他のユーザーのタスク')
        Task.objects.create(user=self.user, title='自分のタスク')
        
        url = reverse('task-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], '自分のタスク')