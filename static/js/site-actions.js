function updateActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll(".main-nav .nav-pill").forEach((link) => {
        const href = link.getAttribute("href");
        if (!href || href === "#") return;
        const isActive = href === "/" ? path === "/" : path.startsWith(href);
        link.classList.toggle("active", isActive);
    });
}

function setupRevealAnimations() {
    const selectors = [
        ".deal-card",
        ".highlight-card",
        ".benefit-card",
        ".dashboard-card",
        ".mock-card",
        ".feature-card",
        ".resource-card",
        ".lesson-card",
        ".surface-panel",
    ];

    const nodes = document.querySelectorAll(selectors.join(","));
    nodes.forEach((node, index) => {
        node.classList.add("reveal", "hover-glow");
        node.style.setProperty("--reveal-delay", `${Math.min(index % 6, 5) * 70}ms`);
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("revealed");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    nodes.forEach((node) => observer.observe(node));
}

function setupHoverGlow() {
    document.querySelectorAll(".hover-glow").forEach((node) => {
        node.addEventListener("pointermove", (event) => {
            const rect = node.getBoundingClientRect();
            node.style.setProperty("--mx", `${event.clientX - rect.left}px`);
            node.style.setProperty("--my", `${event.clientY - rect.top}px`);
        });
    });
}

function setupScrollProgress() {
    const bar = document.querySelector(".scroll-progress-bar");
    if (!bar) return;

    const update = () => {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const ratio = maxScroll > 0 ? window.scrollY / maxScroll : 0;
        bar.style.transform = `scaleX(${Math.min(Math.max(ratio, 0), 1)})`;
    };

    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
}

function setupCountUp() {
    const counters = document.querySelectorAll("[data-countup]");
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const node = entry.target;
            const target = Number(node.dataset.countup || 0);
            let current = 0;
            const step = Math.max(1, Math.ceil(target / 18));
            const tick = () => {
                current = Math.min(target, current + step);
                node.textContent = current;
                if (current < target) {
                    window.requestAnimationFrame(tick);
                }
            };
            tick();
            observer.unobserve(node);
        });
    }, { threshold: 0.4 });
    counters.forEach((counter) => observer.observe(counter));
}

function setupMagneticButtons() {
    document.querySelectorAll(".btn").forEach((button) => {
        button.addEventListener("pointermove", (event) => {
            const rect = button.getBoundingClientRect();
            const x = event.clientX - rect.left - rect.width / 2;
            const y = event.clientY - rect.top - rect.height / 2;
            button.style.transform = `translate(${x * 0.06}px, ${y * 0.08}px)`;
        });
        button.addEventListener("pointerleave", () => {
            button.style.transform = "";
        });
    });
}

function setupParallaxScenes() {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    document.querySelectorAll(".hero-media, .studio-shell, .command-shell").forEach((scene) => {
        const layers = scene.querySelectorAll("[data-parallax]");
        if (!layers.length) return;

        const reset = () => {
            layers.forEach((layer) => {
                layer.style.transform = "";
            });
        };

        scene.addEventListener("pointermove", (event) => {
            const rect = scene.getBoundingClientRect();
            const px = (event.clientX - rect.left) / rect.width - 0.5;
            const py = (event.clientY - rect.top) / rect.height - 0.5;

            layers.forEach((layer) => {
                const strength = Number(layer.dataset.parallaxStrength || 16);
                const tx = px * strength;
                const ty = py * strength;
                layer.style.transform = `(${tx}px, ${ty}px, 0)`;
            });
        });

        scene.addEventListener("pointerleave", reset);
    });
}

function setupTiltCards() {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    document.querySelectorAll(".deal-card, .benefit-card, .highlight-card, .mock-card, .lesson-card").forEach((card) => {
        card.addEventListener("pointermove", (event) => {
            const rect = card.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width - 0.5;
            const y = (event.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(900px) rotateX(${(-y * 5).toFixed(2)}deg) rotateY(${(x * 7).toFixed(2)}deg) translateY(-4px)`;
        });

        card.addEventListener("pointerleave", () => {
            card.style.transform = "";
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    updateActiveNav();
    setupScrollProgress();
    setupRevealAnimations();
    setupHoverGlow();
    setupCountUp();
    setupMagneticButtons();
    setupParallaxScenes();
    setupTiltCards();
});
