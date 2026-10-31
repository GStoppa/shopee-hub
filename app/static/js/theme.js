(function () {
    const savedTheme = localStorage.getItem("shopee_hub_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
})();

document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("theme-toggle-btn");
    if (!toggleBtn) return;

    function atualizarIcone(tema) {
        toggleBtn.textContent = tema === "light" ? "🌙" : "☀️";
        toggleBtn.setAttribute("title", tema === "light" ? "Ativar Modo Escuro" : "Ativar Modo Claro");
    }

    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    atualizarIcone(currentTheme);

    toggleBtn.addEventListener("click", () => {
        document.documentElement.classList.add("theme-transition");

        const atual = document.documentElement.getAttribute("data-theme");
        const novo = atual === "light" ? "dark" : "light";

        document.documentElement.setAttribute("data-theme", novo);
        localStorage.setItem("shopee_hub_theme", novo);
        atualizarIcone(novo);

        setTimeout(() => {
            document.documentElement.classList.remove("theme-transition");
        }, 350);
    });
});