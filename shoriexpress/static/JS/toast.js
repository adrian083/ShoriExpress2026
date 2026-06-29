/**
 * ShoriExpress - Sistema de Notificaciones Toast
 * Notificaciones visuales para acciones CRUD
 */

// Crear contenedor de toasts si no existe
function ensureToastContainer() {
  if (!document.querySelector('.se-toast-container')) {
    const container = document.createElement('div');
    container.className = 'se-toast-container';
    document.body.appendChild(container);
  }
  return document.querySelector('.se-toast-container');
}

/**
 * Mostrar un toast notification
 * @param {string} message - Mensaje del toast
 * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duración en ms (default: 4000)
 * @param {string} title - Título opcional del toast
 */
function showToast(message, type = 'info', duration = 4000, title = null) {
  const container = ensureToastContainer();

  // Determinar icono y título por tipo
  const toastConfig = {
    success: {
      icon: '✓',
      title: title || 'Éxito',
      class: 'success'
    },
    error: {
      icon: '✕',
      title: title || 'Error',
      class: 'error'
    },
    warning: {
      icon: '⚠',
      title: title || 'Advertencia',
      class: 'warning'
    },
    info: {
      icon: 'ℹ',
      title: title || 'Información',
      class: 'info'
    }
  };

  const config = toastConfig[type] || toastConfig.info;

  // Crear elemento del toast
  const toast = document.createElement('div');
  toast.className = `se-toast ${config.class}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'polite');

  const iconAsset = document.createElement('span');
  iconAsset.className = 'se-toast-icon';
  iconAsset.textContent = config.icon;

  const content = document.createElement('div');
  content.className = 'se-toast-content';

  const titleEl = document.createElement('p');
  titleEl.className = 'se-toast-title';
  titleEl.textContent = config.title;

  const msgEl = document.createElement('p');
  msgEl.className = 'se-toast-message';
  msgEl.textContent = message;

  content.appendChild(titleEl);
  content.appendChild(msgEl);

  const closeBtn = document.createElement('button');
  closeBtn.className = 'se-toast-close';
  closeBtn.setAttribute('type', 'button');
  closeBtn.setAttribute('aria-label', 'Cerrar notificación');
  closeBtn.innerHTML = '×';
  closeBtn.addEventListener('click', () => removeToast(toast));

  const progress = document.createElement('div');
  progress.className = 'se-toast-progress';

  toast.appendChild(iconAsset);
  toast.appendChild(content);
  toast.appendChild(closeBtn);
  toast.appendChild(progress);

  container.appendChild(toast);

  // Auto-remover después de la duración
  const timeout = setTimeout(() => {
    if (container.contains(toast)) {
      removeToast(toast);
    }
  }, duration);

  // Guardar timeout en el elemento para limpieza temprana
  toast.dataset.timeoutId = timeout;

  return toast;
}

/**
 * Remover un toast con animación
 */
function removeToast(toastElement) {
  toastElement.classList.add('removing');

  setTimeout(() => {
    const timeoutId = toastElement.dataset.timeoutId;
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (toastElement.parentNode) {
      toastElement.parentNode.removeChild(toastElement);
    }
  }, 300);
}

/**
 * Remover todos los toasts
 */
function removeAllToasts() {
  const container = document.querySelector('.se-toast-container');
  if (container) {
    container.querySelectorAll('.se-toast').forEach(toast => {
      removeToast(toast);
    });
  }
}

/**
 * Procesar mensajes de Django y mostrarlos como toasts
 * Integración automática con el sistema de mensajes de Django
 */
function processDjangoMessages() {
  const messagesList = document.querySelector('[data-django-messages]');
  if (messagesList) {
    const messages = messagesList.getAttribute('data-django-messages');
    if (messages) {
      try {
        const parsed = JSON.parse(messages);
        parsed.forEach(msg => {
          showToast(msg.message, msg.type);
        });
      } catch (e) {
        console.warn('Error parsing Django messages:', e);
      }
    }
  }

  document.querySelectorAll('.django-flash-message').forEach(function (el) {
    const text = el.textContent.trim();
    if (!text) return;
    const tags = (el.dataset.tags || '').split(/\s+/);
    let type = 'info';
    if (tags.includes('error')) type = 'error';
    else if (tags.includes('success')) type = 'success';
    else if (tags.includes('warning')) type = 'warning';
    showToast(text, type);
    if (type === 'success' && text.toLowerCase().includes('agregado')) {
      const cartIcon = document.getElementById('cart-icon-nav');
      if (cartIcon) {
        cartIcon.classList.add('cart-animate');
        setTimeout(() => cartIcon.classList.remove('cart-animate'), 600);
      }
    }
  });

  const flashContainer = document.querySelector('.django-flash-messages');
  if (flashContainer) flashContainer.remove();
}

/**
 * Atajos útiles para mensajes comunes
 */
const Toast = {
  success: (message, title = null) => showToast(message, 'success', 4000, title || 'Éxito'),
  error: (message, title = null) => showToast(message, 'error', 5000, title || 'Error'),
  warning: (message, title = null) => showToast(message, 'warning', 4000, title || 'Advertencia'),
  info: (message, title = null) => showToast(message, 'info', 4000, title || 'Información'),
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Procesar mensajes de Django automáticamente
  processDjangoMessages();

  // Escuchar eventos de formulario
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      // El servidor enviará mensajes que se procesarán en la próxima carga
    });
  });
});

// Exportar para uso global
window.Toast = Toast;
window.showToast = showToast;
window.removeToast = removeToast;
window.removeAllToasts = removeAllToasts;
