document.addEventListener("DOMContentLoaded", () => {
    const movementTypeSelect = document.getElementById("movement_type");
    const quantityInput = document.getElementById("quantity");
    const reasonInput = document.getElementById("reason");

    if (movementTypeSelect && quantityInput && reasonInput) {
        movementTypeSelect.addEventListener("change", (e) => {
            if (e.target.value === "entrada") {
                reasonInput.placeholder = "Ex: Chegada de lote de fornecedor";
            } else if (e.target.value === "saida") {
                reasonInput.placeholder = "Ex: Envio de pedido ou avaria de mercadoria";
            } else if (e.target.value === "ajuste") {
                reasonInput.placeholder = "Ex: Contagem física de balanço";
            }
        });
    }
});