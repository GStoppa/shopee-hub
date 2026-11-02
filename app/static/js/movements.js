document.addEventListener("DOMContentLoaded", () => {
    const movementTypeSelect = document.getElementById("movement_type");
    const quantityInput = document.getElementById("quantity");
    const reasonInput = document.getElementById("reason");
    const hintSpan = document.getElementById("stock-operation-hint");

    if (movementTypeSelect && quantityInput && reasonInput) {
        const currentStock = parseInt(quantityInput.getAttribute("data-current-stock"), 10) || 0;

        function atualizarDica() {
            const tipo = movementTypeSelect.value;
            const qtd = parseInt(quantityInput.value, 10) || 0;

            if (tipo === "entrada") {
                reasonInput.placeholder = "Ex: Chegada de lote de fornecedor";
                quantityInput.removeAttribute("max");
                if (hintSpan) {
                    hintSpan.style.color = "var(--text-muted)";
                    hintSpan.textContent = `Saldo resultante previsto: ${currentStock + qtd} un (saldo atual: ${currentStock} un).`;
                }
            } else if (tipo === "saida") {
                reasonInput.placeholder = "Ex: Envio de pedido, perda ou avaria";
                quantityInput.setAttribute("max", currentStock);
                if (hintSpan) {
                    if (qtd > currentStock) {
                        hintSpan.style.color = "var(--danger)";
                        hintSpan.textContent = `Atenção: Saldo insuficiente! Máximo permitido para saída: ${currentStock} un.`;
                    } else {
                        hintSpan.style.color = "var(--text-muted)";
                        hintSpan.textContent = `Saldo resultante previsto: ${Math.max(0, currentStock - qtd)} un (saldo atual: ${currentStock} un).`;
                    }
                }
            } else if (tipo === "ajuste") {
                reasonInput.placeholder = "Ex: Contagem física de balanço";
                quantityInput.removeAttribute("max");
                if (hintSpan) {
                    const diff = qtd - currentStock;
                    const sinal = diff >= 0 ? `+${diff}` : `${diff}`;
                    hintSpan.style.color = "var(--text-muted)";
                    hintSpan.textContent = `O saldo passará a ser exatamente ${qtd} un (variação de ${sinal} un).`;
                }
            }
        }

        movementTypeSelect.addEventListener("change", atualizarDica);
        quantityInput.addEventListener("input", atualizarDica);
        atualizarDica();
    }
});