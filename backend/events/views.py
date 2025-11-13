from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.conf import settings  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
from .models import Event, EventRegistration, Notification
from .serializers import (
    EventSerializer, EventRegistrationSerializer, 
    NotificationSerializer, UserSerializer, UserRegistrationSerializer
)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet для управления событиями"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at', 'title']
    
    def get_queryset(self):
        """Получение списка событий с фильтрацией"""
        queryset = Event.objects.annotate(
            registered_count=Count('registrations', filter=Q(registrations__status='confirmed'))
        )
        
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        location_filter = self.request.query_params.get('location', None)
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
        
        my_events = self.request.query_params.get('my_events', None)
        if my_events == 'true':
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Создание события - автоматически устанавливаем создателя"""
        event = serializer.save(created_by=self.request.user)
        
        Notification.objects.create(
            user=self.request.user,
            event=event,
            notification_type='registration',
            message=f'Событие "{event.title}" успешно создано'
        )
    
    def perform_update(self, serializer):
        """Обновление события - ПРОВЕРКА ПРАВ"""
        event = self.get_object()
        
        # ✅ ГЛАВНОЕ: Проверяем, что только создатель может редактировать
        if event.created_by != self.request.user:
            raise PermissionDenied(
                detail="Вы не можете редактировать события других пользователей"
            )
        
        updated_event = serializer.save()
        
        # Уведомить всех зарегистрированных пользователей
        registrations = updated_event.registrations.filter(status='confirmed')
        for reg in registrations:
            if reg.user != self.request.user:
                Notification.objects.create(
                    user=reg.user,
                    event=updated_event,
                    notification_type='update',
                    message=f'Событие "{updated_event.title}" было обновлено'
                )
    
    def perform_destroy(self, instance):
        """Удаление события - ПРОВЕРКА ПРАВ"""
        
        # ✅ ГЛАВНОЕ: Проверяем, что только создатель может удалить
        if instance.created_by != self.request.user:
            raise PermissionDenied(
                detail="Вы не можете удалять события других пользователей"
            )
        
        # Уведомить всех зарегистрированных пользователей
        registrations = instance.registrations.filter(status='confirmed')
        for reg in registrations:
            Notification.objects.create(
                user=reg.user,
                event=instance,
                notification_type='cancellation',
                message=f'Событие "{instance.title}" было отменено'
            )
        
        instance.delete()
    
    # ✅ Дополнительная проверка в retrieve (просмотр события)
    def retrieve(self, request, *args, **kwargs):
        """Получить одно событие"""
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Регистрация на событие"""
        event = self.get_object()
        
        if event.is_full():
            return Response(
                {'error': 'Событие заполнено. Все места заняты.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        existing = EventRegistration.objects.filter(
            event=event, 
            user=request.user
        ).first()
        
        if existing:
            if existing.status == 'confirmed':
                return Response(
                    {'error': 'Вы уже зарегистрированы на это событие'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                existing.status = 'confirmed'
                existing.save()
                registration = existing
        else:
            registration = EventRegistration.objects.create(
                event=event,
                user=request.user,
                status='confirmed'
            )
        
        Notification.objects.create(
            user=request.user,
            event=event,
            notification_type='registration',
            message=f'Вы успешно зарегистрированы на событие "{event.title}"'
        )
        
        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        """Отмена регистрации на событие"""
        event = self.get_object()
        
        try:
            registration = EventRegistration.objects.get(
                event=event,
                user=request.user,
                status='confirmed'
            )
            registration.status = 'cancelled'
            registration.save()
            
            Notification.objects.create(
                user=request.user,
                event=event,
                notification_type='cancellation',
                message=f'Вы отменили регистрацию на событие "{event.title}"'
            )
            
            return Response({'message': 'Регистрация успешно отменена'})
        except EventRegistration.DoesNotExist:
            return Response(
                {'error': 'Регистрация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def my_registrations(self, request):
        """Получить события, на которые зарегистрирован пользователь"""
        registrations = EventRegistration.objects.filter(
            user=request.user,
            status='confirmed'
        ).select_related('event')
        
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления уведомлениями"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Получить только уведомления текущего пользователя"""
        queryset = Notification.objects.filter(user=self.request.user)
        
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Отметить уведомление как прочитанное"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Уведомление отмечено как прочитанное'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Отметить все уведомления как прочитанные"""
        count = self.get_queryset().update(is_read=True)
        return Response({'message': f'Отмечено {count} уведомлений'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Получить количество непрочитанных уведомлений"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})


# === АУТЕНТИФИКАЦИЯ С JWT ===

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Регистрация успешна',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Вход пользователя - возвращает JWT токен"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'Необходимо указать имя пользователя и пароль'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    
    return Response(
        {'Неверные учетные данные'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Получить данные текущего пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Запрос на восстановление пароля"""
    email = request.data.get('email')

    if not email:
        return Response(
            {'detail': 'Необходимо указать email'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.filter(email=email).first()
        
        if not user:
            return Response({'message': 'Инструкции отправлены на email'})
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Определяем URL в зависимости от окружения
        if settings.DEBUG:
            frontend_url = "http://localhost:3000"
        else:
            frontend_url = "https://events-sp32.vercel.app"  # Ваш frontend URL
        
        reset_link = f"{frontend_url}/reset-password.html?uid={uid}&token={token}"

        send_mail(
            'Восстановление пароля - Ala-Too Events',
            f'Для сброса пароля перейдите по ссылке: {reset_link}\n\n'
            f'Если вы не запрашивали сброс пароля, проигнорируйте это письмо.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({
            'message': 'Инструкции отправлены на email'
        })
    except Exception as e:
        # В production не показываем детали ошибок
        return Response({
            'message': 'Инструкции отправлены на email'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Сброс пароля по токену"""
    token_str = request.data.get('token', '')
    new_password = request.data.get('password')
    
    if not new_password:
        return Response(
            {'detail': 'Необходимо указать новый пароль'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {'detail': 'Пароль должен содержать минимум 6 символов'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        parts = token_str.split('/')
        if len(parts) != 2:
            raise ValueError("Invalid token format")
        
        uidb64, token = parts
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Пароль успешно изменен'})
        else:
            raise ValueError("Invalid token")
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'detail': 'Недействительная или устаревшая ссылка'},
            status=status.HTTP_400_BAD_REQUEST
        )