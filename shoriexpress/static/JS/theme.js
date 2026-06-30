/**
 * Tema claro/oscuro compartido (cliente y admin).
 */
(function () {
  const STORAGE_KEY = 'shori-theme';

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  function syncButtons() {
    const dark = isDark();
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      const icon = btn.querySelector('[data-theme-icon]') || btn;
      const label = btn.querySelector('[data-theme-label]');
      if (icon && icon !== btn) {
        icon.textContent = dark ? '☀️' : '🌙';
      } else if (!label) {
        btn.textContent = dark ? '☀️' : '🌙';
      }
      if (label) {
        label.textContent = dark ? 'Modo claro' : 'Modo oscuro';
      }
      btn.setAttribute('aria-label', dark ? 'Activar modo claro' : 'Activar modo oscuro');
    });
  }

  function apply(theme) {
    const next = theme === 'dark' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(STORAGE_KEY, next);
    syncButtons();
  }

  function toggle() {
    apply(isDark() ? 'light' : 'dark');
  }

  function init() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
    syncButtons();
  }

  window.ShoriTheme = { apply: apply, toggle: toggle, sync: syncButtons, init: init };
  window.toggleTheme = toggle;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
