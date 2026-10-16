document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("modal-movimento");
    if (!modal) return;

    const openBtns = document.querySelectorAll("[data-action='open-movement-modal']");
    openBtns.forEach((btn) => {
        btn.addEventListener("click", () => modal.classList.add("is-active"));
    });

    const closeBtns = document.querySelectorAll("[data-action='close-movement-modal']");
    closeBtns.forEach((btn) => {
        btn.addEventListener("click", () => modal.classList.remove("is-active"));
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("is-active");
        }
    });
});