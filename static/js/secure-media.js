function appendToken(url) {
    const token = typeof getToken === "function" ? getToken() : "";
    if (!token) return "";
    const separator = url.includes("?") ? "&" : "?";
    return `${url}${separator}token=${encodeURIComponent(token)}`;
}

function activateSecureLessons() {
    if (typeof requireAuth === "function" && !requireAuth()) return;

    const user = typeof getUser === "function" ? getUser() : null;
    const identity = user?.email || user?.username || "secured";

    document.querySelectorAll(".lesson-protected").forEach((card) => {
        const watermark = card.querySelector(".lesson-watermark");
        if (watermark) {
            watermark.textContent = `EduBridge ${identity}`;
        }
    });

    document.querySelectorAll(".secure-video").forEach((video) => {
        const base = video.dataset.secureSrc;
        const source = video.querySelector("source");
        const finalUrl = appendToken(base);
        if (!base || !source || !finalUrl) return;
        source.src = finalUrl;
        video.load();
    });

    document.querySelectorAll(".secure-download-link").forEach((link) => {
        const base = link.dataset.baseHref;
        const finalUrl = appendToken(base);
        if (base && finalUrl) link.href = finalUrl;
    });

    document.querySelectorAll(".lesson-protected").forEach((node) => {
        node.addEventListener("contextmenu", (event) => event.preventDefault());
        node.addEventListener("dragstart", (event) => event.preventDefault());
    });
}

document.addEventListener("DOMContentLoaded", activateSecureLessons);
