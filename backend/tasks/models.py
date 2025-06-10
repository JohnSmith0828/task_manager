# backend/tasks/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Task(models.Model):
    """タスクモデル"""
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='ユーザー'
    )
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1)],
        verbose_name='タイトル'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='説明'
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name='完了状態'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='優先度'
    )
    
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='期限'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='作成日時'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新日時'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'タスク'
        verbose_name_plural = 'タスク'
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def is_overdue(self):
        """期限切れかどうかを判定"""
        if self.due_date and not self.is_completed:
            from django.utils import timezone
            return timezone.now() > self.due_date
        return False