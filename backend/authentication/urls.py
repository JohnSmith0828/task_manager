# backend/authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='user-logout'),
    path('profile/', views.user_profile, name='user-profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
]