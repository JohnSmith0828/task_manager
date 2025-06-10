# backend/tasks/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task


class UserSerializer(serializers.ModelSerializer):
    """ユーザーシリアライザー"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class TaskSerializer(serializers.ModelSerializer):
    """タスクシリアライザー"""
    
    user = UserSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'is_completed',
            'priority', 'due_date', 'created_at', 'updated_at', 'is_overdue'
        ]
    
    def validate_title(self, value):
        """タイトルのバリデーション"""
        if not value.strip():
            raise serializers.ValidationError("タイトルは必須です。")
        return value.strip()
    
    def create(self, validated_data):
        """タスク作成時にユーザーを自動設定"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCreateSerializer(serializers.ModelSerializer):
    """タスク作成専用シリアライザー"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date']
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("タイトルは必須です。")
        return value.strip()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """タスク更新専用シリアライザー"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'is_completed', 'priority', 'due_date']
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("タイトルは必須です。")
        return value.strip()