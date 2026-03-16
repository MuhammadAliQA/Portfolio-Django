// ── EduBridge Mentors Page JS ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.book-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const mentorId   = btn.dataset.mentorId;
            const mentorName = btn.dataset.mentorName;
            openBookingModal(mentorId, mentorName);
        });
    });

    // Modal yopish
    document.getElementById('close-modal')?.addEventListener('click', closeBookingModal);
    document.getElementById('booking-overlay')?.addEventListener('click', (e) => {
        if (e.target.id === 'booking-overlay') closeBookingModal();
    });

    // Booking form
    document.getElementById('booking-form')?.addEventListener('submit', submitBooking);
});

function openBookingModal(mentorId, mentorName) {
    if (typeof isLoggedIn === 'function' && !isLoggedIn()) {
        window.location.href = `/login/?next=/mentors/`;
        return;
    }

    document.getElementById('booking-mentor-id').value   = mentorId;
    document.getElementById('booking-mentor-name').textContent = mentorName;


    const today = new Date().toISOString().split('T')[0];
    document.getElementById('booking-date').min = today;

    document.getElementById('booking-overlay').classList.add('active');
    document.body.style.overflow = 'hidden';


    loadAvailability(mentorId);
}

function closeBookingModal() {
    document.getElementById('booking-overlay').classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('booking-result').textContent = '';
}

async function loadAvailability(mentorId) {
    const select = document.getElementById('booking-time');
    if (!select) return;
    select.innerHTML = '<option>Yuklanmoqda...</option>';

    try {
        const res  = await fetch(`/api/mentors/${mentorId}/availability/`);
        const data = await res.json();

        if (!data.length) {
            select.innerHTML = '<option value="">Bo\'sh vaqt yo\'q</option>';
            return;
        }
        select.innerHTML = data.map(slot =>
            `<option value="${slot.time}" data-date="${slot.date}">
                ${slot.date} — ${slot.time.slice(0,5)}
            </option>`
        ).join('');
    } catch {
        select.innerHTML = '<option value="">Vaqtlarni yuklab bo\'lmadi</option>';
    }
}

async function submitBooking(event) {
    event.preventDefault();

    if (typeof isLoggedIn === 'function' && !isLoggedIn()) {
        window.location.href = '/login/';
        return;
    }

    const btn       = event.target.querySelector('button[type="submit"]');
    const resultEl  = document.getElementById('booking-result');
    btn.disabled    = true;
    btn.textContent = 'Yuborilmoqda...';

    const timeSelect  = document.getElementById('booking-time');
    const selectedOpt = timeSelect.options[timeSelect.selectedIndex];

    const body = {
        mentor:       parseInt(document.getElementById('booking-mentor-id').value),
        date:         selectedOpt?.dataset.date || document.getElementById('booking-date').value,
        time:         timeSelect.value,
        service_type: document.getElementById('booking-service').value,
        goals:        document.getElementById('booking-goals').value.trim(),
    };

    try {
        const res  = await apiFetch('/api/consultations/', {
            method: 'POST',
            body:   JSON.stringify(body),
        });
        const data = await res.json();

        if (res.ok) {
            resultEl.style.color = 'green';
            resultEl.textContent = 'Konsultatsiya muvaffaqiyatli band qilindi!';
            setTimeout(closeBookingModal, 2000);
        } else {
            const msg = Object.values(data).flat().join(' ');
            resultEl.style.color = '#c0392b';
            resultEl.textContent = msg || 'Xato yuz berdi.';
        }
    } catch {
        resultEl.style.color = '#c0392b';
        resultEl.textContent = 'Server bilan bog\'lanishda xato.';
    } finally {
        btn.disabled    = false;
        btn.textContent = 'Tasdiqlash';
    }
}