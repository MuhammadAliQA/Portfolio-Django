document.addEventListener('DOMContentLoaded', async () => {
    if (typeof requireRole === 'function' && !requireRole('student')) return;

    const user = typeof getUser === 'function' ? getUser() : null;
    const nameEl = document.getElementById('user-name');
    if (nameEl && user) nameEl.textContent = user.full_name || user.username;

    const roleEl = document.getElementById('user-role');
    if (roleEl && user) {
        roleEl.textContent = user.role === 'mentor'
            ? (typeof t === 'function' ? t('dashboard.role.mentor', 'Mentor') : 'Mentor')
            : (typeof t === 'function' ? t('dashboard.role.student', 'Student') : 'Student');
    }

    await loadConsultations();
});

async function loadConsultations() {
    const container = document.getElementById('consultations-list');
    if (!container) return;

    container.innerHTML = `
        <div class="dashboard-skeleton">
            <div class="consultation-skeleton"></div>
            <div class="consultation-skeleton"></div>
            <div class="consultation-skeleton"></div>
        </div>
    `;

    try {
        const res = await apiFetch('/api/consultations/');
        const data = await res.json();

        if (!res.ok || (!data.results?.length && !data.length)) {
            container.innerHTML = `<p class="empty-state-text">${typeof t === 'function' ? t('dashboard.empty', "Hali konsultatsiyalar yo'q.") : "Hali konsultatsiyalar yo'q."}</p>`;
            return;
        }

        const items = data.results || data;
        container.innerHTML = items.map((c) => `
            <div class="consultation-card status-${c.status}">
                <div class="c-header">
                    <strong>${c.mentor_name}</strong>
                    <span class="status-badge">${statusLabel(c.status)}</span>
                </div>
                <div class="c-meta">
                    <span>${formatDate(c.date)} — ${c.time?.slice(0, 5)}</span>
                    <span>${serviceLabel(c.service_type)}</span>
                </div>
                ${c.goals ? `<p class="c-goals">${c.goals}</p>` : ''}
                ${c.status === 'pending' || c.status === 'confirmed' ? `
                    <button class="btn btn-sm btn-danger" onclick="cancelConsultation(${c.id})">
                        ${typeof t === 'function' ? t('dashboard.cancel', 'Bekor qilish') : 'Bekor qilish'}
                    </button>` : ''}
            </div>
        `).join('');
    } catch {
        container.innerHTML = `<p class="error-text">${typeof t === 'function' ? t('dashboard.loadError', "Ma'lumot yuklashda xato.") : "Ma'lumot yuklashda xato."}</p>`;
    }
}

async function cancelConsultation(id) {
    if (!confirm(typeof t === 'function' ? t('dashboard.cancelConfirm', 'Konsultatsiyani bekor qilishni tasdiqlaysizmi?') : 'Konsultatsiyani bekor qilishni tasdiqlaysizmi?')) return;
    try {
        const res = await apiFetch(`/api/consultations/${id}/cancel/`, { method: 'POST' });
        if (res.ok) {
            await loadConsultations();
        } else {
            alert(typeof t === 'function' ? t('dashboard.cancelError', 'Bekor qilishda xato yuz berdi.') : 'Bekor qilishda xato yuz berdi.');
        }
    } catch {
        alert(typeof t === 'function' ? t('auth.serverError', "Server bilan bog'lanishda xato.") : "Server bilan bog'lanishda xato.");
    }
}

function statusLabel(s) {
    const map = {
        pending: typeof t === 'function' ? t('dashboard.status.pending', 'Kutilmoqda') : 'Kutilmoqda',
        confirmed: typeof t === 'function' ? t('dashboard.status.confirmed', 'Tasdiqlangan') : 'Tasdiqlangan',
        completed: typeof t === 'function' ? t('dashboard.status.completed', 'Yakunlangan') : 'Yakunlangan',
        cancelled: typeof t === 'function' ? t('dashboard.status.cancelled', 'Bekor qilingan') : 'Bekor qilingan',
    };
    return map[s] || s;
}

function serviceLabel(s) {
    const map = {
        ielts_plan: typeof t === 'function' ? t('dashboard.service.ielts', 'IELTS Plan') : 'IELTS Plan',
        sat_plan: typeof t === 'function' ? t('dashboard.service.sat', 'SAT Plan') : 'SAT Plan',
        admission: typeof t === 'function' ? t('dashboard.service.admission', 'Admission Support') : 'Admission Support',
        essay: typeof t === 'function' ? t('dashboard.service.essay', 'Essay Review') : 'Essay Review',
        career: typeof t === 'function' ? t('dashboard.service.career', 'Career Mapping') : 'Career Mapping',
    };
    return map[s] || s;
}

function formatDate(str) {
    if (!str) return '';
    const d = new Date(str);
    const lang = window.CURRENT_LANG || localStorage.getItem('lang') || 'uz';
    const localeMap = { uz: 'uz-UZ', ru: 'ru-RU', en: 'en-US' };
    return d.toLocaleDateString(localeMap[lang] || 'uz-UZ', { day: '2-digit', month: 'long', year: 'numeric' });
}
