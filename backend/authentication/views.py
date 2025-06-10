# backend/authentication/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


class UserRegistrationView(generics.CreateAPIView):
    """ユーザー登録API"""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """ユーザー登録とトークン発行"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # トークン作成
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'ユーザー登録が完了しました。'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """ユーザーログインAPI"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # トークン取得または作成
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'ログインしました。'
        })
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """ユーザーログアウトAPI"""
    try:
        # トークン削除
        request.user.auth_token.delete()
        logout(request)
        return Response({
            'message': 'ログアウトしました。'
        })
    except:
        return Response({
            'message': 'ログアウトしました。'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """ユーザープロフィール取得API"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """ユーザープロフィール更新API"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'user': serializer.data,
            'message': 'プロフィールを更新しました。'
        })
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )