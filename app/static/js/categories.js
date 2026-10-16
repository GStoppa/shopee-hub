document.addEventListener("DOMContentLoaded", () => {
    const editButtons = document.querySelectorAll("[data-action='toggle-cat-edit']");
    editButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const catId = btn.dataset.id;
            const form = document.getElementById("cat-edit-form-" + catId);
            const display = document.getElementById("cat-name-display-" + catId);

            if (!form || !display) return;

            const isHidden = form.style.display === "none" || form.style.display === "";
            form.style.display = isHidden ? "flex" : "none";
            display.style.display = isHidden ? "none" : "inline";
        });
    });

    const deleteForms = document.querySelectorAll(".form-delete-category");
    deleteForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const name = form.dataset.name || "esta categoria";
            const confirmMsg = `Tem certeza de que deseja excluir a categoria "${name}"? Os produtos vinculados ficarão sem categoria associada.`;
            if (!confirm(confirmMsg)) {
                e.preventDefault();
            }
        });
    });
});