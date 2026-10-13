/**
 * Gestão de Tema (Modo Claro / Modo Escuro)
 */

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('shopee_hub_theme', theme);

    // Atualiza todos os botões de tema presentes na página
    const icons = document.querySelectorAll('.theme-toggle-icon');
    icons.forEach(icon => {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    });
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
}

// Inicializa e sincroniza os ícones assim que o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('shopee_hub_theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    applyTheme(savedTheme);
});