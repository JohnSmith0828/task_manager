# backend/tasks/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Task
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=2,
            help='Number of users to create'
        )
        parser.add_argument(
            '--tasks-per-user',
            type=int,
            default=5,
            help='Number of tasks per user'
        )
    
    def handle(self, *args, **options):
        users_count = options['users']
        tasks_per_user = options['tasks_per_user']
        
        self.stdout.write('Creating sample data...')
        
        # サンプルユーザー作成
        users = []
        for i in range(users_count):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            password = 'testpass123'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'テスト{i+1}',
                    'last_name': 'ユーザー',
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'Created user: {username}')
            else:
                self.stdout.write(f'User already exists: {username}')
            
            users.append(user)
        
        # サンプルタスク作成
        sample_tasks = [
            ('プロジェクトの計画書作成', 'プロジェクトの詳細な計画書を作成する'),
            ('データベース設計', 'アプリケーションのデータベース設計を行う'),
            ('UI/UXデザイン', 'ユーザーインターフェースの設計'),
            ('テストケース作成', '単体テストと結合テストのケース作成'),
            ('ドキュメント作成', 'API仕様書とユーザーマニュアルの作成'),
            ('セキュリティ監査', 'アプリケーションのセキュリティチェック'),
            ('パフォーマンステスト', 'アプリケーションの性能測定'),
            ('デプロイメント準備', '本番環境へのデプロイ準備'),
            ('コードレビュー', 'チームメンバーのコードレビュー'),
            ('定期メンテナンス', 'システムの定期メンテナンス作業'),
        ]
        
        priorities = ['low', 'medium', 'high']
        
        for user in users:
            # 既存のタスクを削除（デモ用）
            Task.objects.filter(user=user).delete()
            
            for i in range(tasks_per_user):
                task_data = random.choice(sample_tasks)
                title = task_data[0]
                description = task_data[1]
                
                # ランダムな期限日を設定
                due_date = None
                if random.choice([True, False]):  # 50%の確率で期限を設定
                    days_ahead = random.randint(1, 30)
                    due_date = datetime.now() + timedelta(days=days_ahead)
                
                task = Task.objects.create(
                    user=user,
                    title=f'{title} ({i+1})',
                    description=description,
                    priority=random.choice(priorities),
                    due_date=due_date,
                    is_completed=random.choice([True, False]) if i > 0 else False
                )
                
                self.stdout.write(f'Created task: {task.title} for {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {users_count} users with {tasks_per_user} tasks each'
            )
        )