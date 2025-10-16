// API Configuration
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : 'https://your-backend.onrender.com/api' // Замените после деплоя backend

// Экспортируем для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_URL;
}

// Для использования в HTML напрямую через <script>
window.API_URL = API_URL