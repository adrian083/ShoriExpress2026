/**
 * Enlaces «agregar al carrito» con toast inmediato (landing / menú).
 */
(function () {
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
    try {
      const url = link.href + (link.href.includes('?') ? '&' : '?') + 'ajax=1';
      const response = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      });
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        if (typeof showToast === 'function') {
          showToast('No se pudo agregar al carrito.', 'error');
        }
        return;
      }
      const data = await response.json();
      if (typeof showToast === 'function' && data.message) {
        showToast(data.message, data.type || (data.success ? 'success' : 'error'));
      }
      if (data.success !== false) {
        updateCartBadge(data.cart_items_count || 0);
        animateCart();
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast('No se pudo agregar al carrito.', 'error');
      }
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
