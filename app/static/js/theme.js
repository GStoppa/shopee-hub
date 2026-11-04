(function () {
    const temaSalvo = localStorage.getItem("stoppa_core_theme") || "dark";
    document.documentElement.setAttribute("data-theme", temaSalvo);
})();

document.addEventListener("DOMContentLoaded", () => {
    const toggleBtns = document.querySelectorAll("#theme-toggle-btn, #theme-toggle, .theme-toggle-btn");
    if (!toggleBtns.length) return;

    function atualizarAcessibilidade(tema) {
        toggleBtns.forEach((btn) => {
            const rotulo = tema === "light" ? "Alternar para Modo Escuro" : "Alternar para Modo Claro";
            btn.setAttribute("title", rotulo);
            btn.setAttribute("aria-label", rotulo);
        });
    }

    const temaAtual = document.documentElement.getAttribute("data-theme") || "dark";
    atualizarAcessibilidade(temaAtual);

    toggleBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            document.documentElement.classList.add("theme-transition");

            const atual = document.documentElement.getAttribute("data-theme") || "dark";
            const proximo = atual === "light" ? "dark" : "light";

            document.documentElement.setAttribute("data-theme", proximo);
            localStorage.setItem("stoppa_core_theme", proximo);
            atualizarAcessibilidade(proximo);

            setTimeout(() => {
                document.documentElement.classList.remove("theme-transition");
            }, 300);
        });
    });
});