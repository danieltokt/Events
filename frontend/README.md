# Event Management System - Frontend

Полнофункциональный фронтенд для системы управления событиями, готовый к интеграции с Django бэкендом.

## 🚀 Возможности

### Реализованные функции
- ✅ Регистрация пользователей с валидацией
- ✅ Вход в систему с опцией "Запомнить меня"
- ✅ Восстановление пароля
- ✅ Сброс пароля
- ✅ Защита страниц (проверка авторизации)
- ✅ Список всех событий
- ✅ Создание событий
- ✅ Редактирование событий
- ✅ Удаление событий (с подтверждением)
- ✅ Просмотр деталей события
- ✅ Поиск событий (БОНУС)
- ✅ Фильтрация по категориям (БОНУС)
- ✅ Сортировка событий (БОНУС)
- ✅ Адаптивный дизайн
- ✅ Уведомления о действиях
- ✅ Обработка ошибок

## 📁 Структура проекта

\`\`\`
frontend/
├── index.html              # Главная (редирект)
├── login.html              # Страница входа
├── register.html           # Страница регистрации
├── forgot-password.html    # Восстановление пароля
├── reset-password.html     # Сброс пароля
├── events.html             # Список событий
├── create-event.html       # Создание события
├── edit-event.html         # Редактирование события
├── view-event.html         # Просмотр события
├── css/
│   └── style.css           # Все стили
└── js/
    ├── utils.js            # Вспомогательные функции
    ├── api.js              # API запросы
    ├── auth.js             # Логика авторизации
    └── events.js           # Логика событий
\`\`\`

## 🔧 Настройка

### 1. Конфигурация API

Откройте файл `js/api.js` и измените `API_BASE_URL` на адрес вашего Django бэкенда:

\`\`\`javascript
const API_BASE_URL = 'http://localhost:8000/api';
\`\`\`

### 2. Ожидаемые API endpoints

Фронтенд ожидает следующие endpoints от Django бэкенда:

#### Авторизация
- `POST /api/auth/register/` - Регистрация
  - Body: `{ email, username, password, confirmPassword }`
  - Response: `{ message, user }`

- `POST /api/auth/login/` - Вход
  - Body: `{ username, password }`
  - Response: `{ token, user: { id, username, email } }`

- `POST /api/auth/forgot-password/` - Восстановление пароля
  - Body: `{ email }`
  - Response: `{ message }`

- `POST /api/auth/reset-password/` - Сброс пароля
  - Body: `{ token, password }`
  - Response: `{ message }`

#### События
- `GET /api/events/` - Получить все события
  - Headers: `Authorization: Bearer {token}`
  - Response: `[{ id, title, description, category, location, start_date, end_date }]`

- `GET /api/events/{id}/` - Получить событие
  - Headers: `Authorization: Bearer {token}`
  - Response: `{ id, title, description, category, location, start_date, end_date }`

- `POST /api/events/` - Создать событие
  - Headers: `Authorization: Bearer {token}`
  - Body: `{ title, description, category, location, start_date, end_date }`
  - Response: `{ id, title, ... }`

- `PUT /api/events/{id}/` - Обновить событие
  - Headers: `Authorization: Bearer {token}`
  - Body: `{ title, description, category, location, start_date, end_date }`
  - Response: `{ id, title, ... }`

- `DELETE /api/events/{id}/` - Удалить событие
  - Headers: `Authorization: Bearer {token}`
  - Response: `204 No Content` или `{ success: true }`

### 3. CORS настройки в Django

Убедитесь, что в вашем Django проекте настроен CORS:

\`\`\`python
# settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Или для разработки:
CORS_ALLOW_ALL_ORIGINS = True
\`\`\`

## 🎨 Дизайн

- Современный и чистый интерфейс
- Адаптивный дизайн (работает на всех устройствах)
- Цветовая схема: Indigo (основной), серый (вторичный), красный (опасность)
- Плавные анимации и переходы
- Доступность (семантический HTML, ARIA)

## 💾 Хранение данных

Приложение использует `localStorage` для хранения:
- `token` - JWT токен авторизации
- `user` - Данные пользователя (JSON)
- `rememberMe` - Флаг "Запомнить меня"

## 🔒 Безопасность

- Валидация на стороне клиента
- Экранирование HTML для предотвращения XSS
- Проверка авторизации на каждой защищенной странице
- Безопасное хранение токенов

## 📱 Адаптивность

Приложение полностью адаптивно и работает на:
- Десктопах (1200px+)
- Планшетах (768px - 1199px)
- Мобильных устройствах (до 767px)

## 🚀 Запуск

Просто откройте `index.html` в браузере или используйте любой локальный сервер:

\`\`\`bash
# Python
python -m http.server 3000

# Node.js
npx serve

# VS Code Live Server
# Установите расширение Live Server и нажмите "Go Live"
\`\`\`

## 📝 Чек-лист функций

- [x] Регистрация работает
- [x] Вход работает
- [x] Токен сохраняется в localStorage
- [x] Защита страниц (редирект если нет токена)
- [x] Создание событий работает
- [x] Просмотр списка событий работает
- [x] Редактирование событий работает
- [x] Удаление событий работает (с подтверждением)
- [x] Все ошибки обрабатываются и показываются пользователю
- [x] Восстановление пароля работает
- [x] Уведомления показываются при действиях
- [x] БОНУС: Поиск работает
- [x] БОНУС: Фильтры работают
- [x] Дизайн адаптивный (работает на мобильных)
- [x] Код чистый и читаемый

## 🔗 Интеграция с Django

### Пример Django View для регистрации:

\`\`\`python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Ваша логика регистрации
    
    return Response({
        'message': 'Регистрация успешна',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })
\`\`\`

### Пример Django View для входа:

\`\`\`python
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return Response(
        {'detail': 'Неверные учетные данные'},
        status=status.HTTP_401_UNAUTHORIZED
    )
\`\`\`

## 🎯 Готово к использованию!

Все функции реализованы и готовы к интеграции с вашим Django бэкендом. Просто настройте API endpoints и наслаждайтесь!
