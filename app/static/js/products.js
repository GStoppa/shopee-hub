document.addEventListener("DOMContentLoaded", () => {
    // 1. Acordeão no Catálogo (Pai / Filhos)
    const accordionRows = document.querySelectorAll(".accordion-row");
    accordionRows.forEach((row) => {
        row.addEventListener("click", (e) => {
            if (e.target.closest("button") || e.target.closest("a") || e.target.closest("form") || e.target.closest("input")) {
                return;
            }
            const prodId = row.dataset.id;
            const subrow = document.getElementById("variants-" + prodId);
            const chevron = document.getElementById("chevron-" + prodId);

            if (subrow) {
                subrow.classList.toggle("is-open");
            }
            if (chevron) {
                chevron.classList.toggle("is-expanded");
            }
        });
    });

    // 2. Confirmação de Exclusão de Anúncio Pai
    const deleteForms = document.querySelectorAll(".form-delete-product");
    deleteForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const name = form.dataset.name || "este produto";
            const confirmMsg = `Tem certeza de que deseja excluir o produto "${name}"? Todas as variações e estoques associados serão removidos.`;
            if (!confirm(confirmMsg)) {
                e.preventDefault();
            }
        });
    });

    // 3. Alternância entre Produto Simples e Grade de Variações
    const typeRadios = document.querySelectorAll('input[name="has_variants"]');
    const simpleBlock = document.getElementById("bloco-simples");
    const variantsBlock = document.getElementById("bloco-variacoes");
    const simpleSku = document.getElementById("simple_sku");
    const simplePrice = document.getElementById("simple_price");

    if (typeRadios.length && simpleBlock && variantsBlock) {
        typeRadios.forEach((radio) => {
            radio.addEventListener("change", () => {
                const comVariacoes = radio.value === "1";
                if (comVariacoes) {
                    simpleBlock.style.display = "none";
                    variantsBlock.style.display = "block";
                    if (simpleSku) simpleSku.removeAttribute("required");
                    if (simplePrice) simplePrice.removeAttribute("required");
                } else {
                    simpleBlock.style.display = "block";
                    variantsBlock.style.display = "none";
                    if (simpleSku) simpleSku.setAttribute("required", "required");
                    if (simplePrice) simplePrice.setAttribute("required", "required");
                }
            });
        });
    }

    // 4. Utilitário: Gerador de UID Determinístico para Linhas
    function gerarUid() {
        return "row_" + Date.now().toString(36) + "_" + Math.random().toString(36).substr(2, 5);
    }

    // 5. Adicionar Linha de Variação no Cadastro
    const btnAddVariant = document.getElementById("btn-add-variant");
    const tbodyVariants = document.getElementById("corpo-variacoes");

    if (btnAddVariant && tbodyVariants) {
        btnAddVariant.addEventListener("click", () => {
            const uid = gerarUid();
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <input type="hidden" name="variant_row_id[]" value="${uid}">
                    <input type="text" name="variant_name[]" class="form-control input-col-name" placeholder="Modelo / Cor" required>
                </td>
                <td><input type="text" name="variant_sku[]" class="form-control input-col-sku" placeholder="SKU" required></td>
                <td><input type="text" name="variant_barcode[]" class="form-control input-col-ean" placeholder="EAN"></td>
                <td><input type="text" name="variant_cost[]" class="form-control input-col-cost" placeholder="0,00"></td>
                <td><input type="text" name="variant_price[]" class="form-control input-col-sale" placeholder="0,00" required></td>
                <td><input type="number" name="variant_stock[]" class="form-control input-col-qty" value="0" min="0"></td>
                <td><input type="number" name="variant_min_stock[]" class="form-control input-col-min" value="5" min="1"></td>
                <td>
                    <div class="file-preview-cell">
                        <div class="preview-thumb-box" id="preview_${uid}">
                            <span class="preview-placeholder-icon">📦</span>
                        </div>
                        <input type="file" name="variant_image_${uid}" accept=".png, .jpg, .jpeg, .webp" class="input-col-file file-preview-input" data-preview-target="preview_${uid}">
                    </div>
                </td>
                <td><button type="button" class="btn-action btn-delete btn-remove-row">✕</button></td>
            `;
            tbodyVariants.appendChild(tr);
        });

        tbodyVariants.addEventListener("click", (e) => {
            if (e.target.classList.contains("btn-remove-row")) {
                if (tbodyVariants.children.length > 1) {
                    e.target.closest("tr").remove();
                } else {
                    alert("É necessário manter pelo menos uma variação.");
                }
            }
        });
    }

    // 6. Adicionar Linha de Nova Variação na Edição
    const btnAddEditVariant = document.getElementById("btn-add-edit-variant");
    const tbodyEditVariants = document.getElementById("corpo-variacoes-edicao");

    if (btnAddEditVariant && tbodyEditVariants) {
        btnAddEditVariant.addEventListener("click", () => {
            const uid = gerarUid();
            const tr = document.createElement("tr");
            tr.classList.add("tr-new-variant");
            tr.innerHTML = `
                <td>
                    <input type="hidden" name="new_variant_row_id[]" value="${uid}">
                    <input type="text" name="new_variant_name[]" class="form-control input-col-name" placeholder="Nova Cor/Tam" required>
                </td>
                <td><input type="text" name="new_variant_sku[]" class="form-control input-col-sku" placeholder="NOVO-SKU" required></td>
                <td><input type="text" name="new_variant_barcode[]" class="form-control input-col-ean" placeholder="EAN"></td>
                <td><input type="text" name="new_variant_cost[]" class="form-control input-col-cost" placeholder="0,00"></td>
                <td><input type="text" name="new_variant_price[]" class="form-control input-col-sale" placeholder="49,90" required></td>
                <td><input type="number" name="new_variant_stock[]" class="form-control input-col-qty" value="0" min="0"></td>
                <td><input type="number" name="new_variant_min_stock[]" class="form-control input-col-min" value="5" min="1"></td>
                <td>
                    <div class="file-preview-cell">
                        <div class="preview-thumb-box" id="preview_new_${uid}">
                            <span class="preview-placeholder-icon">📦</span>
                        </div>
                        <input type="file" name="new_variant_image_${uid}" accept=".png, .jpg, .jpeg, .webp" class="input-col-file file-preview-input" data-preview-target="preview_new_${uid}">
                    </div>
                </td>
                <td class="text-center">
                    <button type="button" class="btn-action btn-delete btn-remove-row" title="Remover linha não salva">✕</button>
                </td>
            `;
            tbodyEditVariants.appendChild(tr);
        });

        tbodyEditVariants.addEventListener("click", (e) => {
            if (e.target.classList.contains("btn-remove-row")) {
                e.target.closest("tr").remove();
            }
        });
    }

    // 7. Exclusão Individual de Variação Existente na Edição
    const deleteVariantBtns = document.querySelectorAll(".btn-delete-single-variant");
    const hiddenDeleteForm = document.getElementById("form-delete-single-variant");

    deleteVariantBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const variantId = btn.dataset.id;
            const variantName = btn.dataset.name || "esta variação";
            const sku = btn.dataset.sku || "";
            const msg = `Tem certeza de que deseja excluir a variação "${variantName}" (${sku})? O estoque e histórico associados serão removidos.`;
            
            if (confirm(msg)) {
                if (hiddenDeleteForm) {
                    hiddenDeleteForm.action = `/products/variant/${variantId}/excluir`;
                    hiddenDeleteForm.submit();
                }
            }
        });
    });

    // 8. Pré-visualização Instantânea de Imagem (Thumbnail Preview)
    document.addEventListener("change", (e) => {
        if (e.target && e.target.classList.contains("file-preview-input")) {
            const file = e.target.files[0];
            const targetId = e.target.dataset.previewTarget;
            const container = document.getElementById(targetId);
            if (!container) return;

            if (file && file.type.startsWith("image/")) {
                const objectUrl = URL.createObjectURL(file);
                container.innerHTML = `<img src="${objectUrl}" alt="Preview" class="variant-thumb">`;
            } else {
                container.innerHTML = `<span class="preview-placeholder-icon">📦</span>`;
            }
        }
    });
});