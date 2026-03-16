function getLessonMessageClasses(type) {
    return type === "error" ? "status-note error-text" : "status-note";
}

function lessonCardMarkup(lesson) {
    const createdBy = lesson.creator_name || "EduBridge";
    const actions = [];
    if (lesson.video_url) {
        actions.push(
            `<a href="${lesson.video_url}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm">${t("lessons.watch", "Videoni ko'rish")}</a>`
        );
    }
    if (lesson.file) {
        actions.push(
            `<a href="${lesson.file}" target="_blank" rel="noopener" class="btn btn-light btn-sm">${t("lessons.download", "Materialni ochish")}</a>`
        );
    }
    actions.push(
        `<button type="button" class="btn btn-danger btn-sm" data-delete-lesson="${lesson.id}">${t("mentorDash.lessons.delete", "Delete")}</button>`
    );

    return `
        <article class="lesson-mini-card">
            <div class="lesson-mini-head">
                <span class="badge">${lesson.track_label || lesson.track}</span>
                <span class="lesson-meta">${t("lessons.by", "Mentor")}: ${createdBy}</span>
            </div>
            <h4>${lesson.title}</h4>
            <p>${lesson.description || ""}</p>
            <div class="lesson-actions">${actions.join("")}</div>
        </article>
    `;
}

async function loadMentorLessons() {
    const list = document.getElementById("mentor-lessons-list");
    if (!list) return;

    try {
        const res = await apiFetch("/api/lessons/?mine=1");
        if (!res.ok) throw new Error("load failed");
        const data = await res.json();
        const lessons = data.results || data;

        if (!lessons.length) {
            list.innerHTML = `<p class="empty-state-text">${t("mentorDash.lessons.empty", "Hali dars yuklanmagan.")}</p>`;
            return;
        }

        list.innerHTML = lessons.map(lessonCardMarkup).join("");
    } catch {
        list.innerHTML = `<p class="error-text">${t("mentorDash.lessons.error", "Lesson yuklashda xato yuz berdi.")}</p>`;
    }
}

async function submitLesson(event) {
    event.preventDefault();

    const user = getUser();
    if (!user || user.role !== "mentor") {
        const message = document.getElementById("lesson-upload-message");
        if (message) {
            message.hidden = false;
            message.className = getLessonMessageClasses("error");
            message.textContent = t("mentorDash.lessons.forbidden", "Bu bo'lim faqat mentorlar uchun.");
        }
        return;
    }

    const form = event.currentTarget;
    const message = document.getElementById("lesson-upload-message");
    const button = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);

    if (!formData.get("file")?.name) {
        formData.delete("file");
    }
    formData.set("is_published", formData.get("is_published") ? "true" : "false");

    button.disabled = true;

    try {
        const token = getToken();
        const res = await fetch("/api/lessons/", {
            method: "POST",
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData,
        });
        const data = await res.json();

        if (!res.ok) {
            const text = Array.isArray(data) ? data.join(" ") : Object.values(data).flat().join(" ");
            throw new Error(text || t("mentorDash.lessons.error", "Lesson yuklashda xato yuz berdi."));
        }

        form.reset();
        const publishField = form.querySelector('input[name="is_published"]');
        if (publishField) publishField.checked = true;

        if (message) {
            message.hidden = false;
            message.className = getLessonMessageClasses("success");
            message.textContent = t("mentorDash.lessons.success", "Lesson muvaffaqiyatli yuklandi.");
        }
        await loadMentorLessons();
    } catch (error) {
        if (message) {
            message.hidden = false;
            message.className = getLessonMessageClasses("error");
            message.textContent = error.message || t("mentorDash.lessons.error", "Lesson yuklashda xato yuz berdi.");
        }
    } finally {
        button.disabled = false;
    }
}

async function deleteLesson(lessonId) {
    const confirmed = window.confirm(t("mentorDash.lessons.deleteConfirm", "Bu videoni o'chirishni tasdiqlaysizmi?"));
    if (!confirmed) return;

    const res = await apiFetch(`/api/lessons/${lessonId}/`, { method: "DELETE" });
    if (!res.ok) {
        window.alert(t("mentorDash.lessons.deleteError", "Lessonni o'chirishda xato yuz berdi."));
        return;
    }
    await loadMentorLessons();
}

document.addEventListener("DOMContentLoaded", () => {
    if (typeof requireRole === "function" && !requireRole("mentor")) return;
    const form = document.getElementById("lesson-upload-form");
    if (!form) return;
    form.addEventListener("submit", submitLesson);
    document.addEventListener("click", (event) => {
        const button = event.target.closest("[data-delete-lesson]");
        if (!button) return;
        deleteLesson(button.dataset.deleteLesson);
    });
    loadMentorLessons();
});
