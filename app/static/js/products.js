document.addEventListener("DOMContentLoaded", () => {
    // 1. Acórdão da Tabela de Catálogo (Expansão de Linhas de Variação)
    const accordionRows = document.querySelectorAll(".accordion-row");
    accordionRows.forEach((row) => {
        row.addEventListener("click", (e) => {
            if (e.target.closest("button") || e.target.closest("a") || e.target.closest("form") || e.target.closest("input")) {
                return;
            }
            const prodId = row.dataset.id;
            const subRow = document.getElementById(`variants-${prodId}`);
            const chevron = document.getElementById(`chevron-${prodId}`);

            if (subRow) subRow.classList.toggle("is-open");
            if (chevron) chevron.classList.toggle("is-expanded");
        });
    });

    // 2. Comutador de Produto Simples vs Com Variações (Inicialização Defensiva)
    const radioVariants = document.querySelectorAll('input[name="has_variants"]');
    const blocoSimples = document.getElementById("bloco-simples");
    const blocoVariacoes = document.getElementById("bloco-variacoes");

    function atualizarEstadoBlocos(comGrade) {
        if (!blocoSimples || !blocoVariacoes) return;

        if (comGrade) {
            blocoSimples.style.display = "none";
            blocoVariacoes.style.display = "block";
            blocoSimples.querySelectorAll("input, select, textarea").forEach((inp) => (inp.disabled = true));
            blocoVariacoes.querySelectorAll("input, select, textarea").forEach((inp) => (inp.disabled = false));
        } else {
            blocoSimples.style.display = "block";
            blocoVariacoes.style.display = "none";
            blocoSimples.querySelectorAll("input, select, textarea").forEach((inp) => (inp.disabled = false));
            blocoVariacoes.querySelectorAll("input, select, textarea").forEach((inp) => (inp.disabled = true));
        }
    }

    if (radioVariants.length > 0) {
        const radioAtivo = document.querySelector('input[name="has_variants"]:checked');
        atualizarEstadoBlocos(radioAtivo && radioAtivo.value === "1");

        radioVariants.forEach((radio) => {
            radio.addEventListener("change", (e) => {
                atualizarEstadoBlocos(e.target.value === "1");
            });
        });
    }

    // 3. Adicionar Nova Linha na Grade (Novo Produto)
    const btnAddVariant = document.getElementById("btn-add-variant");
    const corpoVariacoes = document.getElementById("corpo-variacoes");
    let variantCount = 1;

    if (btnAddVariant && corpoVariacoes) {
        btnAddVariant.addEventListener("click", () => {
            const rowId = `row_${variantCount++}`;
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <input type="hidden" name="variant_row_id[]" value="${rowId}">
                    <input type="text" name="variant_name[]" class="form-control input-col-name" placeholder="Ex: Azul M" required>
                </td>
                <td><input type="text" name="variant_sku[]" class="form-control input-col-sku" placeholder="SKU" required></td>
                <td><input type="text" name="variant_barcode[]" class="form-control input-col-ean" placeholder="EAN"></td>
                <td><input type="text" name="variant_cost[]" class="form-control input-col-cost" placeholder="0,00"></td>
                <td><input type="text" name="variant_price[]" class="form-control input-col-sale" placeholder="49,90" required></td>
                <td><input type="number" name="variant_stock[]" class="form-control input-col-qty" value="0" min="0"></td>
                <td><input type="number" name="variant_min_stock[]" class="form-control input-col-min" value="5" min="1"></td>
                <td>
                    <div class="file-preview-cell">
                        <div class="preview-thumb-box" id="preview_${rowId}">
                            <span class="preview-placeholder-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                                    <circle cx="9" cy="9" r="2"></circle>
                                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
                                </svg>
                            </span>
                        </div>
                        <input type="file" name="variant_image_${rowId}" accept=".png, .jpg, .jpeg, .webp" class="input-col-file file-preview-input" data-preview-target="preview_${rowId}">
                    </div>
                </td>
                <td class="text-center"><button type="button" class="btn-action btn-delete btn-remove-row" title="Remover Linha">✕</button></td>
            `;
            corpoVariacoes.appendChild(tr);
            conectarEventosDeLinha(tr);
            if (window.aplicarMascaras) window.aplicarMascaras(tr);
        });
    }

    // 4. Adicionar Nova Variação (Tela de Edição)
    const btnAddEditVariant = document.getElementById("btn-add-edit-variant");
    const corpoVariacoesEdicao = document.getElementById("corpo-variacoes-edicao");
    let newEditCount = 0;

    if (btnAddEditVariant && corpoVariacoesEdicao) {
        btnAddEditVariant.addEventListener("click", () => {
            const rowId = `new_${newEditCount++}`;
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <input type="hidden" name="new_variant_row_id[]" value="${rowId}">
                    <input type="text" name="new_variant_name[]" class="form-control input-col-name" placeholder="Ex: Vermelho G" required>
                </td>
                <td><input type="text" name="new_variant_sku[]" class="form-control input-col-sku" placeholder="SKU" required></td>
                <td><input type="text" name="new_variant_barcode[]" class="form-control input-col-ean" placeholder="EAN"></td>
                <td><input type="text" name="new_variant_cost[]" class="form-control input-col-cost" placeholder="0,00"></td>
                <td><input type="text" name="new_variant_price[]" class="form-control input-col-sale" placeholder="49,90" required></td>
                <td><input type="number" name="new_variant_stock[]" class="form-control input-col-qty" value="0" min="0"></td>
                <td><input type="number" name="new_variant_min_stock[]" class="form-control input-col-min" value="5" min="1"></td>
                <td>
                    <div class="file-preview-cell">
                        <div class="preview-thumb-box" id="preview_new_${rowId}">
                            <span class="preview-placeholder-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                                    <circle cx="9" cy="9" r="2"></circle>
                                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
                                </svg>
                            </span>
                        </div>
                        <input type="file" name="new_variant_image_${rowId}" accept=".png, .jpg, .jpeg, .webp" class="input-col-file file-preview-input" data-preview-target="preview_new_${rowId}">
                    </div>
                </td>
                <td class="text-center"><button type="button" class="btn-action btn-delete btn-remove-row" title="Remover Linha">✕</button></td>
            `;
            corpoVariacoesEdicao.appendChild(tr);
            conectarEventosDeLinha(tr);
            if (window.aplicarMascaras) window.aplicarMascaras(tr);
        });
    }

    function conectarEventosDeLinha(contexto) {
        contexto.querySelectorAll(".btn-remove-row").forEach((btn) => {
            btn.addEventListener("click", () => {
                const tbody = btn.closest("tbody");
                if (tbody && tbody.querySelectorAll("tr").length <= 1) {
                    alert("A grade deve conter pelo menos uma linha de variação.");
                    return;
                }
                const tr = btn.closest("tr");
                if (tr) tr.remove();
            });
        });

        contexto.querySelectorAll(".file-preview-input").forEach((input) => {
            if (input.dataset.previewConfigured) return;
            input.dataset.previewConfigured = "true";

            input.addEventListener("change", (e) => {
                const targetId = input.dataset.previewTarget;
                const container = document.getElementById(targetId);
                if (!container) return;

                if (e.target.files && e.target.files[0]) {
                    const reader = new FileReader();
                    reader.onload = (re) => {
                        container.innerHTML = `<img src="${re.target.result}" alt="Preview" style="width: 100%; height: 100%; object-fit: cover; border-radius: var(--radius-sm);">`;
                    };
                    reader.readAsDataURL(e.target.files[0]);
                }
            });
        });
    }

    conectarEventosDeLinha(document);

    // 5. Exclusão de Variação Individual com confirmação na tela de edição
    const deleteVariantBtns = document.querySelectorAll(".btn-delete-single-variant");
    const formDeleteVariant = document.getElementById("form-delete-single-variant");

    deleteVariantBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const varId = btn.dataset.id;
            const varName = btn.dataset.name || "esta variação";
            const varSku = btn.dataset.sku || "";

            if (confirm(`Tem certeza de que deseja excluir a variação "${varName}" (SKU: ${varSku})?`)) {
                if (formDeleteVariant) {
                    formDeleteVariant.action = `/products/variant/${varId}/excluir`;
                    formDeleteVariant.submit();
                }
            }
        });
    });

    // 6. Confirmação de Exclusão de Produto Inteiro
    const deleteProductForms = document.querySelectorAll(".form-delete-product");
    deleteProductForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const name = form.dataset.name || "este produto";
            if (!confirm(`Tem certeza de que deseja excluir o produto "${name}" e todas as suas variações?`)) {
                e.preventDefault();
            }
        });
    });

    // Permite clicar diretamente na caixa da miniatura para abrir a seleção de foto
    document.addEventListener("click", (e) => {
        const thumbBox = e.target.closest(".preview-thumb-box");
        if (thumbBox) {
            const container = thumbBox.closest(".file-preview-cell") || thumbBox.closest("td");
            if (container) {
                const fileInput = container.querySelector('input[type="file"]');
                if (fileInput) fileInput.click();
            }
        }
    });
    
});