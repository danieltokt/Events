// API Configuration
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://events-db-h9ge.onrender.com';

// Export for use in other files
window.API_URL = API_URL;