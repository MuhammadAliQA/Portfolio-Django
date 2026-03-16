// ── EduBridge Auth JS ────────────────────────────────────────────────────────
// API base
const API = '';

// ── Foydalanuvchi holatini boshqarish ────────────────────────────────────────
function getToken()   { return localStorage.getItem('access_token'); }
function getUser()    { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } }
function isLoggedIn() { return !!getToken(); }

function saveAuth(data) {
    localStorage.setItem('access_token',  data.access);
    localStorage.setItem('refresh_token', data.refresh);
    if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
}

function clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

// ── Nav holatini yangilash ────────────────────────────────────────────────────
function updateNav() {
    const user      = getUser();
    const loginLink = document.querySelector('a[href="/login/"]');
    const regLink   = document.querySelector('a[href="/register/"]');
    const dashLink  = document.querySelector('a[href="/student-dashboard/"]');

    if (!user || !loginLink) return;

    // Login va Register o'rniga Profil va Chiqish ko'rsatamiz
    loginLink.textContent = user.full_name || user.username;
    loginLink.href = user.role === 'mentor' ? '/mentor-dashboard/' : '/student-dashboard/';

    if (regLink) {
        regLink.textContent = 'Chiqish';
        regLink.href = '#';
        regLink.onclick = (e) => { e.preventDefault(); logout(); };
    }

    if (dashLink) {
        dashLink.href = user.role === 'mentor' ? '/mentor-dashboard/' : '/student-dashboard/';
    }
}

// ── Login ─────────────────────────────────────────────────────────────────────
async function login(event) {
    event.preventDefault();
    const btn = event.target.querySelector('button[type="submit"]');
    btn.disabled    = true;
    btn.textContent = typeof t === 'function' ? t('auth.login.loading', 'Kirish...') : 'Kirish...';

    const body = {
        username: document.getElementById('username').value.trim(),
        password: document.getElementById('password').value,
    };

    try {
        const res  = await fetch(`${API}/api/users/login/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) {
            const msg = data.detail || (typeof t === 'function' ? t('auth.login.invalid', "Username yoki parol noto'g'ri.") : "Username yoki parol noto'g'ri.");
            showError(msg);
            return;
        }

        saveAuth(data);
        const user = data.user || getUser();
        window.location.href = user?.role === 'mentor'
            ? '/mentor-dashboard/'
            : '/student-dashboard/';

    } catch {
        showError(typeof t === 'function' ? t('auth.serverError', "Server bilan bog'lanishda xato.") : "Server bilan bog'lanishda xato.");
    } finally {
        btn.disabled    = false;
        btn.textContent = typeof t === 'function' ? t('auth.login.submit', 'Login') : 'Login';
    }
}

// ── Register ──────────────────────────────────────────────────────────────────
async function register(event) {
    event.preventDefault();
    const btn = event.target.querySelector('button[type="submit"]');
    btn.disabled    = true;
    btn.textContent = typeof t === 'function' ? t('auth.register.loading', "Ro'yxatdan o'tilmoqda...") : "Ro'yxatdan o'tilmoqda...";

    const password  = document.getElementById('password').value;
    const password2 = document.getElementById('password2')?.value;

    if (password2 !== undefined && password !== password2) {
        showError(typeof t === 'function' ? t('auth.register.passwordMismatch', 'Parollar mos kelmadi.') : 'Parollar mos kelmadi.');
        btn.disabled = false;
        btn.textContent = typeof t === 'function' ? t('auth.register.submit', 'Register') : 'Register';
        return;
    }

    const body = {
        username:   document.getElementById('username').value.trim(),
        email:      document.getElementById('email').value.trim(),
        first_name: document.getElementById('first_name')?.value.trim() || '',
        last_name:  document.getElementById('last_name')?.value.trim()  || '',
        role:       document.getElementById('role').value,
        password,
        password2: password2 || password,
    };

    try {
        const res  = await fetch(`${API}/api/users/register/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) {
            const msg = Object.values(data).flat().join(' ');
            showError(msg || (typeof t === 'function' ? t('auth.register.error', "Ro'yxatdan o'tishda xato.") : "Ro'yxatdan o'tishda xato."));
            return;
        }

        // Avtomatik login
        const loginRes  = await fetch(`${API}/api/users/login/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username: body.username, password: body.password }),
        });
        const loginData = await loginRes.json();
        if (loginRes.ok) {
            saveAuth(loginData);
            const user = loginData.user;
            window.location.href = user?.role === 'mentor'
                ? '/mentor-dashboard/'
                : '/student-dashboard/';
        } else {
            window.location.href = '/login/';
        }

    } catch {
        showError(typeof t === 'function' ? t('auth.serverError', "Server bilan bog'lanishda xato.") : "Server bilan bog'lanishda xato.");
    } finally {
        btn.disabled    = false;
        btn.textContent = typeof t === 'function' ? t('auth.register.submit', 'Register') : 'Register';
    }
}

// ── Logout ────────────────────────────────────────────────────────────────────
function logout() {
    clearAuth();
    window.location.href = '/';
}

// ── Auth kerak bo'lgan sahifalar uchun ────────────────────────────────────────
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}

function requireRole(expectedRole) {
    if (!requireAuth()) return false;
    const user = getUser();
    if (!user) {
        window.location.href = '/login/';
        return false;
    }
    if (user.role === expectedRole) return true;
    window.location.href = user.role === 'mentor' ? '/mentor-dashboard/' : '/student-dashboard/';
    return false;
}

// ── API so'rov (token bilan) ──────────────────────────────────────────────────
async function apiFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };
    const res = await fetch(url, { ...options, headers });

    // Token muddati o'tgan bo'lsa, refresh qilish
    if (res.status === 401) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${getToken()}`;
            return fetch(url, { ...options, headers });
        } else {
            clearAuth();
            window.location.href = '/login/';
        }
    }
    return res;
}

async function tryRefreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    try {
        const res  = await fetch(`${API}/api/users/token/refresh/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ refresh }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        localStorage.setItem('access_token', data.access);
        return true;
    } catch { return false; }
}

// ── Xato ko'rsatish ───────────────────────────────────────────────────────────
function showError(msg) {
    let el = document.getElementById('auth-error');
    if (!el) {
        el = document.createElement('p');
        el.id = 'auth-error';
        el.style.cssText = 'color:#c0392b;margin-top:8px;font-size:0.9rem;';
        document.querySelector('.form-stack')?.appendChild(el);
    }
    el.textContent = msg;
}

// ── Sahifa yuklanganda nav yangilanadi ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', updateNav);
