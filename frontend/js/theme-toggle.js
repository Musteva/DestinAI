// Theme Toggle Logic
// 1. On load, check localStorage or system preference
// 2. Toggle class 'dark' on <html>
// 3. Save preference to localStorage

(function () {
    // Helper to set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
        updateIcon(theme);
    }

    // Helper to update button icon
    function updateIcon(theme) {
        const btn = document.getElementById('theme-toggle-btn');
        if (!btn) return;

        // Simple SVG icons for Moon (Dark) and Sun (Light)
        const moonIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" /></svg>`;
        const sunIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" /></svg>`;

        btn.innerHTML = theme === 'dark' ? sunIcon : moonIcon;
    }

    // Initialize
    const savedTheme = localStorage.getItem('theme');
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');

    // Apply immediately to avoid flash
    if (initialTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }

    // Wait for DOM to insert button if not present
    window.addEventListener('DOMContentLoaded', () => {
        let btn = document.getElementById('theme-toggle-btn');
        if (!btn) {
            btn = document.createElement('button');
            btn.id = 'theme-toggle-btn';
            btn.className = "fixed bottom-5 right-5 p-3 rounded-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white shadow-lg hover:shadow-xl transition-all z-50 border border-gray-200 dark:border-gray-700";
            btn.onclick = () => {
                const isDark = document.documentElement.classList.contains('dark');
                setTheme(isDark ? 'light' : 'dark');
            };
            document.body.appendChild(btn);
        }
        updateIcon(initialTheme);
    });

})();
