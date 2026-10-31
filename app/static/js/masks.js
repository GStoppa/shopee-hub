(function () {
    function formatarMoeda(valor) {
        if (!valor) return "";
        let v = valor.toString().replace(/\D/g, "");
        if (v === "") return "";
        v = (parseInt(v, 10) / 100).toFixed(2) + "";
        v = v.replace(".", ",");
        v = v.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.");
        return v;
    }

    function formatarDocumento(valor) {
        let v = valor.replace(/\D/g, "").slice(0, 14);
        if (v.length <= 11) {
            // CPF: 000.000.000-00
            v = v.replace(/(\d{3})(\d)/, "$1.$2");
            v = v.replace(/(\d{3})(\d)/, "$1.$2");
            v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
        } else {
            // CNPJ: 00.000.000/0001-00
            v = v.replace(/^(\d{2})(\d)/, "$1.$2");
            v = v.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2");
            v = v.replace(/\.(\d{3})(\d)/, ".$1/$2");
            v = v.replace(/(\d{4})(\d{1,2})$/, "$1-$2");
        }
        return v;
    }

    function formatarTelefone(valor) {
        let v = valor.replace(/\D/g, "").slice(0, 11);
        if (v.length > 10) {
            // Celular: (00) 00000-0000
            v = v.replace(/^(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3");
        } else if (v.length > 5) {
            // Fixo: (00) 0000-0000
            v = v.replace(/^(\d{2})(\d{4})(\d{0,4})$/, "($1) $2-$3");
        } else if (v.length > 2) {
            v = v.replace(/^(\d{2})(\d+)/, "($1) $2");
        } else if (v.length > 0) {
            v = v.replace(/^(\d+)/, "($1");
        }
        return v;
    }

    function aplicarMascaras(contexto = document) {
        // 1. Custo e Preço de Venda (R$)
        const priceInputs = contexto.querySelectorAll('input[name*="price"], input[name*="cost"]');
        priceInputs.forEach((input) => {
            if (input.dataset.maskConfigured) return;
            input.dataset.maskConfigured = "true";

            input.addEventListener("input", (e) => {
                e.target.value = formatarMoeda(e.target.value);
            });
        });

        // 2. Números inteiros (Estoque inicial, estoque mínimo e ajustes)
        const integerInputs = contexto.querySelectorAll(
            'input[name*="stock"], input[name^="v_stock_"], input[name^="v_min_"], input[name*="_min_stock"], input[name="quantity"]'
        );
        integerInputs.forEach((input) => {
            if (input.dataset.maskConfigured) return;
            input.dataset.maskConfigured = "true";

            input.addEventListener("input", (e) => {
                e.target.value = e.target.value.replace(/[^0-9]/g, "");
            });
        });

        // 3. Medidas decimais (Logística: peso em gramas e dimensões em cm)
        const decimalInputs = contexto.querySelectorAll(
            'input[name="weight_g"], input[name="length_cm"], input[name="width_cm"], input[name="height_cm"]'
        );
        decimalInputs.forEach((input) => {
            if (input.dataset.maskConfigured) return;
            input.dataset.maskConfigured = "true";

            input.addEventListener("input", (e) => {
                let val = e.target.value.replace(/[^0-9,.]/g, "");
                val = val.replace(".", ",");
                const partes = val.split(",");
                if (partes.length > 2) {
                    val = partes[0] + "," + partes.slice(1).join("");
                }
                e.target.value = val;
            });
        });

        // 4. CPF / CNPJ (Loja)
        const docInputs = contexto.querySelectorAll('input[name="document"], #document');
        docInputs.forEach((input) => {
            if (input.dataset.maskConfigured) return;
            input.dataset.maskConfigured = "true";

            input.addEventListener("input", (e) => {
                e.target.value = formatarDocumento(e.target.value);
            });
        });

        // 5. Telefone / WhatsApp (Loja)
        const phoneInputs = contexto.querySelectorAll('input[name="phone"], #phone');
        phoneInputs.forEach((input) => {
            if (input.dataset.maskConfigured) return;
            input.dataset.maskConfigured = "true";

            input.addEventListener("input", (e) => {
                e.target.value = formatarTelefone(e.target.value);
            });
        });
    }

    window.aplicarMascaras = aplicarMascaras;

    document.addEventListener("DOMContentLoaded", () => {
        aplicarMascaras(document);
    });
})();