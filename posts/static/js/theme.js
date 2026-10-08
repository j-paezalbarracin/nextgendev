function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    actualizarIconoTema(newTheme);
    console.log(`🌓 Tema cambiado a: ${newTheme}`);
}

function actualizarIconoTema(theme) {
    const icon = document.getElementById('theme-icon');
    if (!icon) return;
    
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';  // ☀️
    } else {
        icon.className = 'fas fa-moon'; // 🌙
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    actualizarIconoTema(currentTheme);
    
    console.log(`🌓 Tema inicial: ${currentTheme}`);
    
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            actualizarIconoTema(newTheme);
        }
    });
});