/**
 * Feedback inmediato al enviar formularios del panel (antes del redirect).
 */
(function () {
  function notify(message, type) {
    if (typeof window.showToast === 'function') {
      window.showToast(message, type || 'info', 2500);
    }
  }

  function init() {
    document.querySelectorAll('form[method="post"], form[method="POST"]').forEach(function (form) {
      if (form.dataset.notifyBound === '1') return;
      if (form.classList.contains('cart-qty-form')) return;
      form.dataset.notifyBound = '1';
      form.addEventListener('submit', function () {
        const isDelete = (form.action || '').includes('eliminar') ||
          form.querySelector('button[type="submit"], input[type="submit"]')?.textContent?.toLowerCase().includes('eliminar');
        if (isDelete) {
          notify('Eliminando…', 'info');
        } else {
          notify('Guardando cambios…', 'info');
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
