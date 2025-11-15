from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создание роутера
router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Маршруты из роутера
    path('', include(router.urls)),
    
    # === Аутентификация (путь /api/auth/) ===
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/current-user/', views.current_user, name='current-user'),
    path('auth/forgot-password/', views.forgot_password, name='forgot-password'),
    path('auth/reset-password/', views.reset_password, name='reset-password'),
    path('auth/create-admin/', views.create_superuser_temp, name='create-admin'),
]