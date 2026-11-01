(function () {
    const temaSalvo = localStorage.getItem("shopee_hub_theme") || "dark";
    document.documentElement.setAttribute("data-theme", temaSalvo);
})();

document.addEventListener("DOMContentLoaded", () => {
    const toggleBtns = document.querySelectorAll("#theme-toggle-btn, #theme-toggle, .theme-toggle-btn");
    if (!toggleBtns.length) return;

    function atualizarIcones(tema) {
        toggleBtns.forEach((btn) => {
            const indicador = btn.querySelector(".theme-icon-indicator") || btn;
            indicador.textContent = tema === "light" ? "🌙" : "☀️";
            btn.setAttribute("title", tema === "light" ? "Mudar para Modo Escuro" : "Mudar para Modo Claro");
            btn.setAttribute("aria-label", tema === "light" ? "Mudar para Modo Escuro" : "Mudar para Modo Claro");
        });
    }

    const temaAtual = document.documentElement.getAttribute("data-theme") || "dark";
    atualizarIcones(temaAtual);

    toggleBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            document.documentElement.classList.add("theme-transition");

            const atual = document.documentElement.getAttribute("data-theme") || "dark";
            const proximo = atual === "light" ? "dark" : "light";

            document.documentElement.setAttribute("data-theme", proximo);
            localStorage.setItem("shopee_hub_theme", proximo);
            atualizarIcones(proximo);

            setTimeout(() => {
                document.documentElement.classList.remove("theme-transition");
            }, 300);
        });
    });
});