# backend/authentication/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


class UserRegistrationTest(APITestCase):
    """ユーザー登録の単体テスト"""
    
    def setUp(self):
        self.registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
    
    def test_successful_registration(self):
        """正常なユーザー登録テスト"""
        url = reverse('user-register')
        response = self.client.post(url, self.registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
    
    def test_password_mismatch(self):
        """パスワード不一致テスト"""
        self.registration_data['password_confirm'] = 'DifferentPass123!'
        
        url = reverse('user-register')
        response = self.client.post(url, self.registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_duplicate_username(self):
        """ユーザー名重複テスト"""
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='password123'
        )
        
        url = reverse('user-register')
        response = self.client.post(url, self.registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)


class UserLoginTest(APITestCase):
    """ユーザーログインの結合テスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_successful_login(self):
        """正常なログインテスト"""
        url = reverse('user-login')
        response = self.client.post(url, self.login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
    
    def test_invalid_credentials(self):
        """不正な認証情報テスト"""
        self.login_data['password'] = 'wrongpassword'
        
        url = reverse('user-login')
        response = self.client.post(url, self.login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_credentials(self):
        """認証情報不足テスト"""
        url = reverse('user-login')
        response = self.client.post(url, {'username': 'testuser'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTest(APITestCase):
    """ユーザーログアウトテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    
    def test_successful_logout(self):
        """正常なログアウトテスト"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        url = reverse('user-logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # トークンが削除されているかチェック
        self.assertFalse(Token.objects.filter(user=self.user).exists())
    
    def test_logout_without_auth(self):
        """認証なしログアウトテスト"""
        url = reverse('user-logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)