from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, EventRegistration, Notification


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор для события"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    # ✅ ДОБАВЛЕНО: ID создателя для проверки прав на фронте
    created_by_id = serializers.SerializerMethodField()
    registered_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    # ✅ ДОБАВЛЕНО: Проверка является ли текущий пользователь владельцем
    is_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'location', 'start_date', 'end_date', 
            'status', 'capacity', 'created_by', 'created_by_id', 'created_by_name', 
            'registered_count', 'is_registered', 'is_full', 'is_owner',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_created_by_id(self, obj):
        """Возвращает ID создателя события"""
        return obj.created_by.id
    
    def get_is_owner(self, obj):
        """Проверяет, является ли текущий пользователь владельцем события"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.created_by == request.user
        return False
    
    def get_is_registered(self, obj):
        """Проверка регистрации текущего пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EventRegistration.objects.filter(
                event=obj, 
                user=request.user, 
                status='confirmed'
            ).exists()
        return False
    
    def get_registered_count(self, obj):
        """Получить количество зарегистрированных"""
        return obj.get_registered_count()
    
    def get_is_full(self, obj):
        """Проверка заполненности события"""
        return obj.is_full()
    
    def validate(self, data):
        """Валидация дат"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    "end_date": "Дата окончания должна быть позже даты начала"
                })
        
        if data.get('capacity') and data['capacity'] < 1:
            raise serializers.ValidationError({
                "capacity": "Вместимость должна быть больше 0"
            })
        
        return data


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации на событие"""
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_start_date = serializers.DateTimeField(source='event.start_date', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = [
            'id', 'event', 'event_title', 'event_start_date',
            'user', 'user_name', 'status', 'registered_at'
        ]
        read_only_fields = ['user', 'registered_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений"""
    event_title = serializers.CharField(source='event.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'event', 'event_title', 'notification_type', 
            'message', 'is_read', 'created_at'
        ]
        read_only_fields = ['created_at']