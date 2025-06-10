# backend/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ユーザー登録シリアライザー"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, attrs):
        """パスワード確認のバリデーション"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("パスワードが一致しません。")
        return attrs
    
    def validate_username(self, value):
        """ユーザー名の重複チェック"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("このユーザー名は既に使用されています。")
        return value
    
    def validate_email(self, value):
        """メールアドレスの重複チェック"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスは既に使用されています。")
        return value
    
    def create(self, validated_data):
        """ユーザー作成"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """ユーザーログインシリアライザー"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """認証情報の検証"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("ユーザー名またはパスワードが間違っています。")
            if not user.is_active:
                raise serializers.ValidationError("このアカウントは無効です。")
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("ユーザー名とパスワードを入力してください。")


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報シリアライザー"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']