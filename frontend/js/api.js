// API Configuration
const API_BASE_URL = "http://localhost:8000/api"

// Helper function to get auth headers
function getAuthHeaders() {
  const token = localStorage.getItem("token")
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  }
}

// Helper function to handle API errors
async function handleResponse(response) {
  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    // Если это валидация от DRF (например, {password_confirm: ["Обязательное поле."]})
    if (typeof data === "object" && Object.keys(data).length > 0) {
      throw data   // вернём весь объект ошибок
    }

    throw new Error(data.message || data.detail || "Произошла ошибка")
  }

  return data
}


// Auth API calls
async function apiRegister(email, username, password, confirmPassword) {
  const response = await fetch(`${API_BASE_URL}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      username,
      password,
    }),
  })
  return handleResponse(response)
}


async function apiLogin(username, password) {
  console.log('apiLogin called with:', username);
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    
    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);
    
    const data = await handleResponse(response);
    console.log('Response data:', data);
    
    return data;
  } catch (error) {
    console.error('apiLogin error:', error);
    throw error;
  }
}

async function apiForgotPassword(email) {
  const response = await fetch(`${API_BASE_URL}/auth/forgot-password/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
  return handleResponse(response)
}

async function apiResetPassword(token, password) {
  const response = await fetch(`${API_BASE_URL}/auth/reset-password/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, password }),
  })
  return handleResponse(response)
}

// Events API calls
async function apiGetEvents() {
  console.log('Запрос на получение событий...');
  console.log('Token:', localStorage.getItem('token'));
  
  const response = await fetch(`${API_BASE_URL}/events/`, {
    method: "GET",
    headers: getAuthHeaders(),
  })
  
  console.log('Response status:', response.status);
  
  const data = await handleResponse(response);
  
  // ИСПРАВЛЕНИЕ: Возвращаем только массив results, а не весь объект
  return data.results || [];
}

async function apiGetEvent(id) {
  const response = await fetch(`${API_BASE_URL}/events/${id}/`, {
    method: "GET",
    headers: getAuthHeaders(),
  })
  return handleResponse(response)
}

async function apiCreateEvent(eventData) {
  const response = await fetch(`${API_BASE_URL}/events/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(eventData),
  })
  return handleResponse(response)
}

async function apiUpdateEvent(id, eventData) {
  const response = await fetch(`${API_BASE_URL}/events/${id}/`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(eventData),
  })
  return handleResponse(response)
}

async function apiDeleteEvent(id) {
  const response = await fetch(`${API_BASE_URL}/events/${id}/`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.message || error.detail || "Произошла ошибка")
  }

  // DELETE может вернуть 204 No Content
  if (response.status === 204) {
    return { success: true }
  }

  return response.json()
}