/**
 * Remove o alerta com transição de opacidade e encolhimento vertical.
 * @param {HTMLElement} botao - O botão de fecho clicado.
 */
function fecharAlerta(botao) {
    const alerta = botao.closest(".alert");
    if (!alerta) return;

    alerta.style.transition = "opacity 0.2s ease, transform 0.2s ease, max-height 0.25s ease, margin 0.2s ease, padding 0.2s ease";
    alerta.style.opacity = "0";
    alerta.style.transform = "translateY(-6px)";
    alerta.style.maxHeight = alerta.offsetHeight + "px";

    setTimeout(() => {
        alerta.style.maxHeight = "0px";
        alerta.style.paddingTop = "0px";
        alerta.style.paddingBottom = "0px";
        alerta.style.marginTop = "0px";
        alerta.style.marginBottom = "0px";
    }, 50);

    setTimeout(() => {
        alerta.remove();
        const container = document.querySelector(".alerts-container");
        if (container && container.querySelectorAll(".alert").length === 0) {
            container.remove();
        }
    }, 260);
}

document.addEventListener("DOMContentLoaded", () => {
    // 1. Menu Mobile (Gaveta Lateral e Máscara de Fundo)
    const mobileBtn = document.getElementById("mobile-menu-btn");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");

    function abrirMenuMobile() {
        if (sidebar) sidebar.classList.add("is-open");
        if (overlay) overlay.classList.add("is-active");
        document.body.style.overflow = "hidden";
    }

    function fecharMenuMobile() {
        if (sidebar) sidebar.classList.remove("is-open");
        if (overlay) overlay.classList.remove("is-active");
        document.body.style.overflow = "";
    }

    if (mobileBtn) {
        mobileBtn.addEventListener("click", () => {
            const aberto = sidebar && sidebar.classList.contains("is-open");
            if (aberto) fecharMenuMobile();
            else abrirMenuMobile();
        });
    }

    if (overlay) {
        overlay.addEventListener("click", fecharMenuMobile);
    }

    // Fecha o menu ao redimensionar para ecrãs de computador
    window.addEventListener("resize", () => {
        if (window.innerWidth > 1024) {
            fecharMenuMobile();
        }
    });

    // 2. Delegação de clique de fecho para alertas dinâmicos
    document.addEventListener("click", (e) => {
        const btn = e.target.closest(".alert-close");
        if (btn) {
            fecharAlerta(btn);
        }
    });

    // 3. Dispensar alertas automaticamente após 6 segundos
    const alertas = document.querySelectorAll(".alert");
    alertas.forEach((alerta) => {
        setTimeout(() => {
            if (document.body.contains(alerta)) {
                const btn = alerta.querySelector(".alert-close");
                if (btn) fecharAlerta(btn);
            }
        }, 6000);
    });
});