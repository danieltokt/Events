// ===========================
// Authentication functions
// ===========================

// Register user
async function register(email, username, password, confirmPassword) {
    const response = await fetch(`${window.API_URL}/api/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, password, password_confirm: confirmPassword })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw errorData;
    }

    return response.json();
}

// Login user
async function login(username, password, rememberMe = false) {
    try {
        const data = await apiLogin(username, password);

        console.log('Login response:', data);

        if (!data) throw new Error('Сервер вернул пустой ответ');

        const token = data.token || data.access;
        if (!token) throw new Error('Токен не получен от сервера');

        localStorage.setItem("token", token);
        if (data.user) localStorage.setItem("user", JSON.stringify(data.user));
        if (rememberMe) localStorage.setItem("rememberMe", "true");

        showNotification("Вход выполнен успешно!", "success");
        setTimeout(() => window.location.href = "events.html", 1000);
    } catch (error) {
        console.error('Login error:', error);
        const formError = document.getElementById("formError");
        if (formError) formError.textContent = error.message || JSON.stringify(error);
        showNotification(error.message || "Ошибка входа", "error");
        throw error;
    }
}

// Logout user
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("rememberMe");
    showNotification("Вы вышли из системы", "info");
    setTimeout(() => window.location.href = "login.html", 1000);
}

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem("user");
    if (!userStr) return null;
    try {
        return JSON.parse(userStr);
    } catch (error) {
        return null;
    }
}

// Forgot password
async function forgotPassword(email) {
    try {
        await apiForgotPassword(email);
        showNotification("Ссылка для восстановления отправлена на email", "success");
    } catch (error) {
        const formError = document.getElementById("formError");
        if (formError) formError.textContent = error.message || JSON.stringify(error);
        showNotification(error.message || "Ошибка", "error");
        throw error;
    }
}

// Reset password
async function resetPassword(token, password) {
    try {
        await apiResetPassword(token, password);
        showNotification("Пароль успешно изменен! Перенаправление...", "success");
        setTimeout(() => window.location.href = "login.html", 1500);
    } catch (error) {
        const formError = document.getElementById("formError");
        if (formError) formError.textContent = error.message || JSON.stringify(error);
        showNotification(error.message || "Ошибка", "error");
        throw error;
    }
}

// Helper functions
function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
}

function showFieldError(fieldId, message) {
    const el = document.getElementById(fieldId);
    if (el) el.textContent = message;
}

// ===========================
// Registration form handler
// ===========================
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        clearErrors();

        const email = document.getElementById('email').value.trim();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        let hasError = false;

        if (!email) {
            showFieldError('emailError', 'Email обязателен');
            hasError = true;
        }
        if (!username) {
            showFieldError('usernameError', 'Имя пользователя обязательно');
            hasError = true;
        }
        if (password.length < 6) {
            showFieldError('passwordError', 'Пароль должен содержать минимум 6 символов');
            hasError = true;
        }
        if (password !== confirmPassword) {
            showFieldError('confirmPasswordError', 'Пароли не совпадают');
            hasError = true;
        }

        if (hasError) {
            if (window.birdMascot) window.birdMascot.sad();
            return;
        }

        const btn = document.getElementById('registerBtn');
        btn.disabled = true;
        btn.textContent = 'Регистрация...';
        if (window.birdMascot) window.birdMascot.loading();

        try {
            await register(email, username, password, confirmPassword);

            if (window.birdMascot) {
                window.birdMascot.stopLoading();
                window.birdMascot.happy();
            }

            btn.textContent = 'Зарегистрировано!';
            setTimeout(() => window.location.href = "login.html", 1000);

        } catch (error) {
            if (window.birdMascot) {
                window.birdMascot.stopLoading();
                window.birdMascot.error();
            }
            btn.disabled = false;
            btn.textContent = 'Зарегистрироваться';

            if (error) {
                for (let key in error) {
                    const fieldErrorId = key + "Error"; 
                    const msg = Array.isArray(error[key]) ? error[key][0] : error[key];
                    const el = document.getElementById(fieldErrorId);
                    if (el) el.textContent = msg;
                }
            }
        }
    });
}