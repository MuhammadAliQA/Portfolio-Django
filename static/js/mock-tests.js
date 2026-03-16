let currentExam = null;
let timerId = null;
let remainingSeconds = 0;
let examStarted = false;
let activeUtterance = null;

function setStageLoading(isLoading) {
    const loader = document.getElementById("mock-stage-loading");
    const form = document.getElementById("mock-test-form");
    const startBtn = document.getElementById("start-exam");
    const submitBtn = document.getElementById("submit-exam");
    if (loader) loader.hidden = !isLoading;
    if (form) form.hidden = isLoading;
    if (startBtn) startBtn.disabled = isLoading || !currentExam;
    if (submitBtn && isLoading) submitBtn.disabled = true;
}

function setTimerLabel() {
    const timer = document.getElementById("exam-timer");
    if (!timer) return;
    if (!remainingSeconds && remainingSeconds !== 0) {
        timer.textContent = "--:--";
        return;
    }
    const minutes = String(Math.floor(remainingSeconds / 60)).padStart(2, "0");
    const seconds = String(remainingSeconds % 60).padStart(2, "0");
    timer.textContent = `${minutes}:${seconds}`;
}

function startTimer(minutes) {
    window.clearInterval(timerId);
    remainingSeconds = (minutes || 0) * 60;
    setTimerLabel();
    timerId = window.setInterval(() => {
        if (remainingSeconds <= 0) {
            window.clearInterval(timerId);
            return;
        }
        remainingSeconds -= 1;
        setTimerLabel();
    }, 1000);
}

function renderExam(exam) {
    currentExam = exam;
    examStarted = false;
    window.speechSynthesis?.cancel();
    activeUtterance = null;
    document.getElementById("exam-title").textContent = exam.title;
    document.getElementById("exam-description").textContent = exam.description || "Mock test tayyor.";
    const form = document.getElementById("mock-test-form");
    const startBtn = document.getElementById("start-exam");
    const submitBtn = document.getElementById("submit-exam");
    const result = document.getElementById("mock-result");
    result.hidden = true;
    result.className = "mock-result";
    result.innerHTML = "";
    startBtn.disabled = false;
    submitBtn.disabled = true;
    remainingSeconds = 0;
    setTimerLabel();
    setStageLoading(false);

    const isListening = String(exam.section || "").toLowerCase().includes("listening");
    form.innerHTML = exam.questions.map((question, index) => `
        <fieldset class="mock-question">
            <legend>${index + 1}. ${question.prompt}</legend>
            ${isListening ? `
                <div class="mock-audio-block">
                    <button type="button" class="btn btn-secondary btn-sm" data-play-audio="${index}">
                        Play audio
                    </button>
                    <button type="button" class="btn btn-light btn-sm" data-toggle-transcript="${index}">
                        Transcript
                    </button>
                    <div class="mock-transcript" id="transcript-${index}" hidden>${question.context_text || ""}</div>
                </div>
            ` : question.context_text ? `<div class="mock-context">${question.context_text}</div>` : ""}
            <div class="mock-options">
                ${question.choices.map((choice) => `
                    <label class="mock-option">
                        <input type="radio" name="question-${question.id}" value="${choice.id}">
                        <span>${choice.text}</span>
                    </label>
                `).join("")}
            </div>
        </fieldset>
    `).join("");

    document.querySelectorAll("[data-exam-card]").forEach((card) => {
        card.classList.toggle("active", Number(card.dataset.examId) === exam.id);
    });

    window.clearInterval(timerId);
    bindAudioControls(exam);
}

function bindAudioControls(exam) {
    document.querySelectorAll("[data-play-audio]").forEach((button) => {
        button.addEventListener("click", () => {
            const index = Number(button.dataset.playAudio);
            const question = exam.questions[index];
            if (!question) return;
            const text = question.context_text || question.prompt;
            if (!("speechSynthesis" in window)) {
                window.alert("Browser voice support mavjud emas.");
                return;
            }
            window.speechSynthesis.cancel();
            activeUtterance = new SpeechSynthesisUtterance(text);
            activeUtterance.lang = "en-US";
            activeUtterance.rate = 0.92;
            window.speechSynthesis.speak(activeUtterance);
        });
    });

    document.querySelectorAll("[data-toggle-transcript]").forEach((button) => {
        button.addEventListener("click", () => {
            const index = Number(button.dataset.toggleTranscript);
            const transcript = document.getElementById(`transcript-${index}`);
            if (!transcript) return;
            transcript.hidden = !transcript.hidden;
        });
    });
}

async function loadExam(examId) {
    setStageLoading(true);
    const res = await fetch(`/api/assessments/exams/${examId}/`);
    if (!res.ok) {
        setStageLoading(false);
        return;
    }
    const exam = await res.json();
    renderExam(exam);
}

async function submitExam() {
    if (!currentExam || !examStarted) return;
    if (typeof requireAuth === "function" && !requireAuth()) return;

    const answers = currentExam.questions.map((question) => {
        const selected = document.querySelector(`input[name="question-${question.id}"]:checked`);
        return selected ? { question: question.id, choice: Number(selected.value) } : null;
    }).filter(Boolean);

    const res = await apiFetch(`/api/assessments/exams/${currentExam.id}/submit/`, {
        method: "POST",
        body: JSON.stringify({ answers }),
    });
    const data = await res.json();
    const result = document.getElementById("mock-result");
    result.hidden = false;

    if (!res.ok) {
        result.className = "mock-result error-text";
        result.textContent = data.error || "Testni yuborishda xato yuz berdi.";
        return;
    }

    result.className = "mock-result result-live";
    result.innerHTML = `
        <strong>${data.exam_title}</strong>
        <p>Natija: ${data.score}/${data.max_score} · ${data.percentage}%</p>
    `;
    window.clearInterval(timerId);
}

document.addEventListener("DOMContentLoaded", () => {
    const firstExam = document.querySelector("[data-load-exam]");
    if (firstExam) loadExam(firstExam.dataset.loadExam);

    document.querySelectorAll("[data-load-exam]").forEach((button) => {
        button.addEventListener("click", () => loadExam(button.dataset.loadExam));
    });

    document.getElementById("start-exam")?.addEventListener("click", () => {
        if (!currentExam) return;
        examStarted = true;
        document.getElementById("submit-exam").disabled = false;
        document.getElementById("start-exam").disabled = true;
        startTimer(currentExam.duration_minutes);
    });

    document.getElementById("submit-exam")?.addEventListener("click", submitExam);
});
