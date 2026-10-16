document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert-box");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-6px)";
            setTimeout(() => alert.remove(), 300);
        }, 4000);

        const closeBtn = alert.querySelector(".alert-close-btn");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => alert.remove());
        }
    });

    const forms = document.querySelectorAll("form");
    forms.forEach((form) => {
        form.addEventListener("submit", () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                setTimeout(() => {
                    submitBtn.disabled = true;
                    submitBtn.style.opacity = "0.7";
                    submitBtn.style.cursor = "not-allowed";
                }, 10);
            }
        });
    });
});