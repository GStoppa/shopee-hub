document.addEventListener("DOMContentLoaded", () => {
    const deleteCategoryForms = document.querySelectorAll(".form-delete-category");
    deleteCategoryForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const name = form.dataset.name || "esta categoria";
            if (!confirm(`Tem certeza de que deseja excluir a categoria "${name}"? Os produtos vinculados ficarão sem categoria.`)) {
                e.preventDefault();
            }
        });
    });
});