document.addEventListener("DOMContentLoaded", () => {
    function formatarMoeda(valor) {
        let digitos = valor.replace(/\D/g, "");
        if (!digitos) return "";
        let numero = (parseInt(digitos, 10) / 100).toFixed(2);
        let partes = numero.split(".");
        partes[0] = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        return partes.join(",");
    }

    function formatarDocumento(valor) {
        let v = valor.replace(/\D/g, "").slice(0, 14);
        if (v.length <= 11) {
            return v
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
        } else {
            return v
                .replace(/^(\d{2})(\d)/, "$1.$2")
                .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
                .replace(/\.(\d{3})(\d)/, ".$1/$2")
                .replace(/(\d{4})(\d)/, "$1-$2");
        }
    }

    function formatarTelefone(valor) {
        let v = valor.replace(/\D/g, "").slice(0, 11);
        if (v.length <= 10) {
            return v
                .replace(/^(\d{2})(\d)/g, "($1) $2")
                .replace(/(\d{4})(\d)/, "$1-$2");
        } else {
            return v
                .replace(/^(\d{2})(\d)/g, "($1) $2")
                .replace(/(\d{5})(\d)/, "$1-$2");
        }
    }

    document.addEventListener("input", (e) => {
        const el = e.target;
        if (!el || el.tagName !== "INPUT") return;

        const name = el.name || "";
        if (
            el.classList.contains("mask-currency") ||
            name.includes("price") ||
            name.includes("cost") ||
            name.startsWith("v_price_") ||
            name.startsWith("v_cost_")
        ) {
            el.value = formatarMoeda(el.value);
        }

        if (el.id === "document" || el.classList.contains("mask-document")) {
            el.value = formatarDocumento(el.value);
        }

        if (el.id === "phone" || el.classList.contains("mask-phone")) {
            el.value = formatarTelefone(el.value);
        }
    });
});