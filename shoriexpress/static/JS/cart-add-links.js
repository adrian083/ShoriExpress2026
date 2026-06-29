/**
 * Menú / landing: agregar al carrito con toast inmediato (sin recargar).
 */
(function () {
  function notify(message, type) {
    if (typeof window.showToast === 'function') {
      window.showToast(message, type || 'info');
    } else if (typeof window.notifyUser === 'function') {
      window.notifyUser(message, type || 'info');
    }
  }

  function updateCartBadge(count) {
    document.querySelectorAll('.cart-badge').forEach(function (badge) {
      if (count > 0) {
        badge.textContent = count;
        badge.style.display = '';
      } else {
        badge.style.display = 'none';
      }
    });
  }

  function animateCart() {
    const cartIcon = document.getElementById('cart-icon-nav');
    if (cartIcon) {
      cartIcon.classList.add('cart-animate');
      setTimeout(function () {
        cartIcon.classList.remove('cart-animate');
      }, 600);
    }
  }

  async function addToCart(event, link) {
    if (document.getElementById('cart-items-body')) return;
    event.preventDefault();
    notify('Agregando al carrito…', 'info');
    try {
      const url = link.href + (link.href.indexOf('?') >= 0 ? '&' : '?') + 'ajax=1';
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      });
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        notify('No se pudo agregar al carrito.', 'error');
        return;
      }
      const data = await response.json();
      if (data.message) {
        notify(data.message, data.type || (data.success ? 'success' : 'error'));
      }
      if (data.success !== false) {
        updateCartBadge(data.cart_items_count || 0);
        animateCart();
      }
    } catch (err) {
      notify('No se pudo agregar al carrito.', 'error');
    }
  }

  function init() {
    document.querySelectorAll('a[href*="/carrito/agregar/"]').forEach(function (link) {
      if (link.dataset.cartBound === '1') return;
      link.dataset.cartBound = '1';
      link.addEventListener('click', function (e) {
        addToCart(e, link);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
