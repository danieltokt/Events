from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Event(models.Model):
    """Модель события"""
    STATUS_CHOICES = [
        ('upcoming', 'Предстоящее'),
        ('ongoing', 'Проходит'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    CATEGORY_CHOICES = [
        ('conference', 'Конференция'),
        ('workshop', 'Праздничное событие'),
        ('meetup', 'Собрание'),
        ('webinar', 'Вебинар'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        blank=True,
        verbose_name='Категория'
    )
    location = models.CharField(max_length=200, blank=True, verbose_name='Место проведения')
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='upcoming', 
        verbose_name='Статус'
    )
    capacity = models.IntegerField(default=100, verbose_name='Вместимость')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_events', 
        verbose_name='Создатель'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        ordering = ['-start_date', '-created_at']  
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
    
    def __str__(self):
        return self.title
    
    def get_registered_count(self):
        """Количество подтвержденных регистраций"""
        return self.registrations.filter(status='confirmed').count()
    
    def is_full(self):
        """Проверка заполненности события"""
        return self.get_registered_count() >= self.capacity


class EventRegistration(models.Model):
    """Модель регистрации на событие"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ]
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='registrations', 
        verbose_name='Событие'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='event_registrations', 
        verbose_name='Пользователь'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='confirmed', 
        verbose_name='Статус'
    )
    registered_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Зарегистрирован'
    )
    
    class Meta:
        unique_together = ['event', 'user']
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Notification(models.Model):
    """Модель уведомлений"""
    TYPE_CHOICES = [
        ('registration', 'Регистрация'),
        ('reminder', 'Напоминание'),
        ('cancellation', 'Отмена'),
        ('update', 'Обновление'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications', 
        verbose_name='Пользователь'
    )
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name='Событие'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        verbose_name='Тип'
    )
    message = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"