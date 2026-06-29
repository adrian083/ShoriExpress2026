/**
 * Acciones del carrito vía AJAX: toast inmediato y actualización sin error del host.
 */
(function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : '';
  }

  function formatMoney(num) {
    try {
      return new Intl.NumberFormat('es-CO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(num);
    } catch (e) {
      return (Math.round(num * 100) / 100).toFixed(2);
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

  function renderCartTable(items) {
    const tbody = document.getElementById('cart-items-body');
    if (!tbody) return;

    if (!items.length) {
      tbody.innerHTML =
        '<tr><td colspan="5">' +
        '<div class="empty-cart">' +
        '<div class="empty-cart-icon">🛒</div>' +
        '<h3>Tu carrito está vacío</h3>' +
        '<p>Parece que aún no has agregado productos a tu carrito.</p>' +
        '<a href="/#menu" class="se-btn se-btn-primary">Ver Menú</a>' +
        '</div></td></tr>';
      return;
    }

    const csrf = getCookie('csrftoken');
  const rows = items.map(function (item) {
      const restarUrl = '/productos/carrito/restar/' + item.producto_id + '/';
      const agregarUrl =
        '/productos/carrito/agregar/' + item.producto_id + '/?next=/carrito/&ajax=1';
      const eliminarUrl = '/productos/carrito/eliminar/' + item.producto_id + '/';
      return (
        '<tr data-product-id="' + item.producto_id + '">' +
        '<td><span class="product-name">' + item.nombre + '</span></td>' +
        '<td class="text-center"><div class="quantity-controls">' +
        '<form method="post" action="' + restarUrl + '" class="cart-qty-form">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrf + '">' +
        '<input type="hidden" name="ajax" value="1">' +
        '<button type="submit" class="se-btn se-btn-outline se-btn-sm" title="Quitar una unidad">−</button>' +
        '</form>' +
        '<span class="quantity-badge">' + item.cantidad + '</span>' +
        '<a href="' + agregarUrl + '" class="se-btn se-btn-outline se-btn-sm cart-add-link" title="Agregar una unidad">+</a>' +
        '</div></td>' +
        '<td class="price-cell">$' + item.precio + '</td>' +
        '<td class="total-cell">$' + item.total + '</td>' +
        '<td class="text-center">' +
        '<form method="post" action="' + eliminarUrl + '" class="cart-qty-form">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrf + '">' +
        '<input type="hidden" name="ajax" value="1">' +
        '<button type="submit" class="se-btn se-btn-outline-red se-btn-sm" title="Eliminar del carrito">🗑️</button>' +
        '</form></td></tr>'
      );
    }).join('');

    tbody.innerHTML = rows;
    bindCartForms(tbody);
    bindCartAddLinks(tbody);
  }

  function updateTotals(data) {
    const subtotal = document.getElementById('cart-subtotal');
    const total = document.getElementById('cart-total');
    const display = '$' + formatMoney(data.cart_total || 0);
    if (subtotal) subtotal.textContent = display;
    if (total) total.textContent = display;
    updateCartBadge(data.cart_items_count || 0);

    const totalSin = document.getElementById('total-sin-descuento');
    if (totalSin) totalSin.value = data.cart_total_display || data.cart_total;
  }

  async function submitCartForm(form) {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) btn.disabled = true;
    try {
      const formData = new FormData(form);
      formData.set('ajax', '1');
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      });
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        if (typeof showToast === 'function') {
          showToast('No se pudo actualizar el carrito. Recarga la página.', 'error');
        }
        return;
      }
      const data = await response.json();
      if (typeof showToast === 'function' && data.message) {
        showToast(data.message, data.type || (data.success ? 'success' : 'error'));
      }
      if (data.success !== false) {
        if (!data.items || !data.items.length) {
          window.location.reload();
          return;
        }
        renderCartTable(data.items || []);
        updateTotals(data);
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast('No se pudo actualizar el carrito. Recarga la página.', 'error');
      }
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  async function addToCart(url) {
    try {
      const sep = url.includes('?') ? '&' : '?';
      const response = await fetch(url + sep + 'ajax=1', {
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
        renderCartTable(data.items || []);
        updateTotals(data);
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast('No se pudo agregar al carrito.', 'error');
      }
    }
  }

  function bindCartForms(root) {
    (root || document).querySelectorAll('.cart-qty-form').forEach(function (form) {
      if (form.dataset.bound === '1') return;
      form.dataset.bound = '1';
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        submitCartForm(form);
      });
    });
  }

  function bindCartAddLinks(root) {
    (root || document).querySelectorAll('.cart-add-link, a[href*="/carrito/agregar/"]').forEach(function (link) {
      if (link.dataset.bound === '1') return;
      link.dataset.bound = '1';
      link.addEventListener('click', function (e) {
        if (!document.getElementById('cart-items-body')) return;
        e.preventDefault();
        addToCart(link.href);
      });
    });
  }

  function bindClearCart() {
    const form = document.getElementById('form-vaciar-carrito');
    if (!form || form.dataset.bound === '1') return;
    form.dataset.bound = '1';
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      submitCartForm(form);
    });
  }

  function init() {
    bindCartForms(document);
    bindCartAddLinks(document);
    bindClearCart();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
