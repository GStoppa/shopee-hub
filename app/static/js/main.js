document.addEventListener("DOMContentLoaded", () => {
    // 1. Auto-dismiss de mensagens de alerta após 4 segundos
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

    // 2. Prevenção de envio duplo em formulários (Double Submit)
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

    // 3. Menu Lateral Responsivo (Mobile Drawer)
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const sidebar = document.querySelector(".sidebar");
    const sidebarOverlay = document.getElementById("sidebar-overlay");

    function fecharSidebarMobile() {
        if (sidebar) sidebar.classList.remove("is-open");
        if (sidebarOverlay) sidebarOverlay.classList.remove("is-active");
    }

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener("click", () => {
            sidebar.classList.toggle("is-open");
            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle("is-active");
            }
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", fecharSidebarMobile);
    }

    // 4. Confirmação de Exclusão de Membro da Equipe
    const deleteMemberForms = document.querySelectorAll(".form-delete-member");
    deleteMemberForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const name = form.dataset.name || "este membro";
            if (!confirm(`Tem certeza de que deseja remover o acesso de "${name}"?`)) {
                e.preventDefault();
            }
        });
    });
});