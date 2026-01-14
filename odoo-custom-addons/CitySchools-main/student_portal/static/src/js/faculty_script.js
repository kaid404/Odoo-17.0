document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light-theme';
    document.body.className = currentTheme;

    themeToggleBtn.addEventListener('click', () => {
        if (document.body.classList.contains('light-theme')) {
            document.body.className = 'dark-theme';
            localStorage.setItem('theme', 'dark-theme');
        } else {
            document.body.className = 'light-theme';
            localStorage.setItem('theme', 'light-theme');
        }
    });
});
