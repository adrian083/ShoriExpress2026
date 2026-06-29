/**
 * Carrito: GET para +/- (como agregar), cantidad manual, toasts al instante.
 */
(function () {
  function cfg() {
    return window.ShoriCartConfig || {};
  }

  function getCsrf() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function notify(message, type) {
    if (typeof window.showToast === 'function') {
      window.showToast(message, type || 'info');
    } else if (typeof window.notifyUser === 'function') {
      window.notifyUser(message, type || 'info');
    }
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

  function urlFor(kind, productId) {
    const urls = cfg().urls || {};
    const pattern = urls[kind];
    if (!pattern) return '';
    return pattern.replace('__ID__', productId);
  }

  function withAjax(url) {
    return url + (url.indexOf('?') >= 0 ? '&' : '?') + 'ajax=1';
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

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function renderCartTable(items) {
    const tbody = document.getElementById('cart-items-body');
    if (!tbody) return;

    if (!items.length) {
      window.location.reload();
      return;
    }

    const rows = items.map(function (item) {
      const pid = item.producto_id;
      return (
        '<tr data-product-id="' + pid + '">' +
        '<td><span class="product-name">' + escapeHtml(item.nombre) + '</span></td>' +
        '<td class="text-center"><div class="quantity-controls">' +
        '<a href="' + withAjax(urlFor('restar', pid)) + '" class="se-btn se-btn-outline se-btn-sm cart-restar-link" title="Quitar una unidad">−</a>' +
        '<input type="number" min="1" max="999" class="cart-qty-input" value="' + item.cantidad + '" ' +
        'data-product-id="' + pid + '" aria-label="Cantidad de ' + escapeHtml(item.nombre) + '" title="Escribe la cantidad y presiona Enter">' +
        '<a href="' + withAjax(urlFor('agregar', pid) + '?next=/carrito/') + '" class="se-btn se-btn-outline se-btn-sm cart-add-link" title="Agregar una unidad">+</a>' +
        '</div></td>' +
        '<td class="price-cell">$' + escapeHtml(String(item.precio)) + '</td>' +
        '<td class="total-cell">$' + escapeHtml(String(item.total)) + '</td>' +
        '<td class="text-center">' +
        '<a href="' + withAjax(urlFor('eliminar', pid)) + '" class="se-btn se-btn-outline-red se-btn-sm cart-remove-link" title="Eliminar del carrito">🗑️</a>' +
        '</td></tr>'
      );
    }).join('');

    tbody.innerHTML = rows;
    bindAll(tbody);
  }

  function updateTotals(data) {
    const display = '$' + formatMoney(data.cart_total || 0);
    const subtotal = document.getElementById('cart-subtotal');
    const total = document.getElementById('cart-total');
    if (subtotal) subtotal.textContent = display;
    if (total) total.textContent = display;
    updateCartBadge(data.cart_items_count || 0);
    const totalSin = document.getElementById('total-sin-descuento');
    if (totalSin) totalSin.value = data.cart_total_display || data.cart_total;
  }

  async function parseCartResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      throw new Error('non-json');
    }
    return response.json();
  }

  async function cartGet(url) {
    const response = await fetch(withAjax(url), {
      method: 'GET',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin',
    });
    return parseCartResponse(response);
  }

  async function cartPost(url, body) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCsrf(),
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body,
      credentials: 'same-origin',
    });
    return parseCartResponse(response);
  }

  async function applyCartData(data) {
    if (data.message) {
      notify(data.message, data.type || (data.success ? 'success' : 'error'));
    }
    if (data.success === false) return;
    if (!data.items || !data.items.length) {
      window.location.reload();
      return;
    }
    renderCartTable(data.items);
    updateTotals(data);
  }

  async function handleCartLink(event, link) {
    event.preventDefault();
    try {
      const data = await cartGet(link.getAttribute('href') || link.href);
      await applyCartData(data);
    } catch (err) {
      notify('No se pudo actualizar el carrito. Recarga la página.', 'error');
    }
  }

  async function handleQtyInput(input) {
    const productId = input.dataset.productId;
    const cantidad = parseInt(input.value, 10);
    if (!productId || Number.isNaN(cantidad) || cantidad < 0) {
      notify('Ingresa una cantidad válida.', 'error');
      return;
    }
    input.disabled = true;
    try {
      const url = urlFor('cantidad', productId);
      const data = await cartPost(withAjax(url), 'cantidad=' + encodeURIComponent(cantidad) + '&ajax=1');
      await applyCartData(data);
    } catch (err) {
      notify('No se pudo actualizar la cantidad.', 'error');
    } finally {
      input.disabled = false;
    }
  }

  async function handleClearCart(event) {
    event.preventDefault();
    if (!window.confirm('¿Vaciar todo el carrito?')) return;
    try {
      const url = (cfg().urls && cfg().urls.limpiar) || '';
      const data = await cartGet(url);
      await applyCartData(data);
    } catch (err) {
      notify('No se pudo vaciar el carrito.', 'error');
    }
  }

  function bindQtyInputs(root) {
    (root || document).querySelectorAll('.cart-qty-input').forEach(function (input) {
      if (input.dataset.bound === '1') return;
      input.dataset.bound = '1';
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          input.blur();
        }
      });
      input.addEventListener('change', function () {
        handleQtyInput(input);
      });
    });
  }

  function bindCartLinks(root, selector) {
    (root || document).querySelectorAll(selector).forEach(function (link) {
      if (link.dataset.bound === '1') return;
      link.dataset.bound = '1';
      link.addEventListener('click', function (e) {
        handleCartLink(e, link);
      });
    });
  }

  function bindAll(root) {
    bindCartLinks(root, '.cart-restar-link, .cart-add-link, .cart-remove-link');
    bindQtyInputs(root);
  }

  function init() {
    bindAll(document);
    const clearBtn = document.getElementById('btn-vaciar-carrito');
    if (clearBtn && clearBtn.dataset.bound !== '1') {
      clearBtn.dataset.bound = '1';
      clearBtn.addEventListener('click', handleClearCart);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
