(function () {
    // 1. Aplica o tema imediatamente na abertura da página para evitar cintilação inicial
    const temaGuardado = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", temaGuardado);

    function atualizarIcone(tema) {
        const icone = document.getElementById("theme-icon");
        if (icone) {
            icone.textContent = tema === "light" ? "🌙" : "☀️";
        }
    }

    function inicializarAlternadorTema() {
        const botao = document.getElementById("theme-toggle");
        const temaAtual = document.documentElement.getAttribute("data-theme") || "dark";
        atualizarIcone(temaAtual);

        if (!botao) return;

        botao.addEventListener("click", () => {
            const temaAtivo = document.documentElement.getAttribute("data-theme") || "dark";
            const novoTema = temaAtivo === "dark" ? "light" : "dark";

            // Injeta a classe que ativa a interpolação suave
            document.documentElement.classList.add("theme-transition");

            document.documentElement.setAttribute("data-theme", novoTema);
            localStorage.setItem("theme", novoTema);
            atualizarIcone(novoTema);

            // Remove a classe após a conclusão do efeito
            setTimeout(() => {
                document.documentElement.classList.remove("theme-transition");
            }, 380);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", inicializarAlternadorTema);
    } else {
        inicializarAlternadorTema();
    }
})();