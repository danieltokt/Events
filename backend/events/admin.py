from django.contrib import admin
from .models import Event, EventRegistration, Notification


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Админ-панель для событий"""
    list_display = ['title', 'location', 'start_date', 'end_date', 'status', 'capacity', 'created_by', 'created_at']
    list_filter = ['status', 'start_date', 'location']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at', 'registered_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'location')
        }),
        ('Даты и статус', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Вместимость', {
            'fields': ('capacity', 'registered_count')
        }),
        ('Создатель', {
            'fields': ('created_by',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def registered_count(self, obj):
        """Отображение количества зарегистрированных"""
        return obj.registered_count()
    registered_count.short_description = 'Зарегистрировано'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """Админ-панель для регистраций"""
    list_display = ['event', 'user', 'status', 'registered_at']
    list_filter = ['status', 'registered_at', 'event__status']
    search_fields = ['event__title', 'user__username', 'user__email']
    readonly_fields = ['registered_at']
    
    fieldsets = (
        ('Регистрация', {
            'fields': ('event', 'user', 'status')
        }),
        ('Информация', {
            'fields': ('registered_at',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Админ-панель для уведомлений"""
    list_display = ['user', 'notification_type', 'event', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message', 'event__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Уведомление', {
            'fields': ('user', 'event', 'notification_type', 'message')
        }),
        ('Статус', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Массовое действие: отметить как прочитанное"""
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} уведомлений отмечено как прочитанные')
    mark_as_read.short_description = 'Отметить как прочитанные'
    
    def mark_as_unread(self, request, queryset):
        """Массовое действие: отметить как непрочитанное"""
        count = queryset.update(is_read=False)
        self.message_user(request, f'{count} уведомлений отмечено как непрочитанные')
    mark_as_unread.short_description = 'Отметить как непрочитанные'