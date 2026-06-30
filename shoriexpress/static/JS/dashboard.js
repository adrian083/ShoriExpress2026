let chartVentasDia = null;
let chartPedidosEstado = null;
let chartProductosTop = null;
let chartTipoPedido = null;
let ultimoPedidoConocido = null;
let timeoutOcultarAlerta = null;

const COLORS = {
    red: '#DC2626',
    redLight: 'rgba(220, 38, 38, 0.75)',
    dark: '#111111',
    darkLight: 'rgba(17, 17, 17, 0.65)',
    success: '#16A34A',
    successLight: 'rgba(22, 163, 74, 0.75)',
    warning: '#D97706',
    warningLight: 'rgba(217, 119, 6, 0.75)',
    info: '#2563EB',
    infoLight: 'rgba(37, 99, 235, 0.75)',
    neutral: '#6B7280',
    neutralLight: 'rgba(107, 114, 128, 0.35)',
};

const ESTADO_COLORS = {
    pendiente: { bg: COLORS.warningLight, border: COLORS.warning },
    preparacion: { bg: COLORS.infoLight, border: COLORS.info },
    listo: { bg: COLORS.successLight, border: COLORS.success },
    entregado: { bg: 'rgba(22, 163, 74, 0.55)', border: COLORS.success },
    cancelado: { bg: COLORS.redLight, border: COLORS.red },
};

const ESTADO_LABELS = {
    pendiente: 'Pendiente',
    preparacion: 'En preparación',
    listo: 'Listo',
    entregado: 'Entregado',
    cancelado: 'Cancelado',
};

const TIPO_LABELS = {
    local: 'Para comer aquí',
    llevar: 'Para llevar',
    domicilio: 'Domicilio',
};

function isDarkTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
}

function chartThemeOptions() {
    const dark = isDarkTheme();
    return {
        text: dark ? '#e5e5e5' : '#374151',
        grid: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
        border: dark ? '#404040' : '#ffffff',
    };
}

function formatCurrency(value) {
    return '$' + Number(value || 0).toLocaleString('es-CO', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    });
}

function destroyChart(chartRef) {
    if (chartRef) {
        chartRef.destroy();
    }
    return null;
}

function showChartEmpty(canvasId, message) {
    const wrap = document.getElementById(canvasId)?.closest('.dash-chart-wrap');
    if (!wrap) return;
    let note = wrap.querySelector('.dash-chart-empty');
    if (!note) {
        note = document.createElement('p');
        note.className = 'dash-chart-empty';
        wrap.appendChild(note);
    }
    note.textContent = message;
    note.hidden = false;
}

function hideChartEmpty(canvasId) {
    const wrap = document.getElementById(canvasId)?.closest('.dash-chart-wrap');
    const note = wrap?.querySelector('.dash-chart-empty');
    if (note) note.hidden = true;
}

function setDefaultDates() {
    const hoy = new Date();
    const hace30 = new Date();
    hace30.setDate(hoy.getDate() - 30);

    const inputInicio = document.getElementById('filtroFechaInicio');
    const inputFin = document.getElementById('filtroFechaFin');

    if (inputInicio && !inputInicio.value) {
        inputInicio.value = hace30.toISOString().split('T')[0];
    }
    if (inputFin && !inputFin.value) {
        inputFin.value = hoy.toISOString().split('T')[0];
    }
}

function resetFiltros() {
    document.getElementById('filtroFechaInicio').value = '';
    document.getElementById('filtroFechaFin').value = '';
    setDefaultDates();
    cargarDashboard();
}

function cargarDashboard() {
    const fechaInicio = document.getElementById('filtroFechaInicio').value;
    const fechaFin = document.getElementById('filtroFechaFin').value;

    let url = '/dashboard/api/dashboard-data/?';
    if (fechaInicio) url += 'fecha_inicio=' + encodeURIComponent(fechaInicio) + '&';
    if (fechaFin) url += 'fecha_fin=' + encodeURIComponent(fechaFin);

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => {
            if (!response.ok) {
                throw new Error('Respuesta no OK en dashboard-data: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            actualizarKPIs(data.kpis);
            renderChartVentasDia(data.ventas_por_dia || []);
            renderChartPedidosEstado(data.pedidos_por_estado || []);
            renderChartProductosTop(data.productos_top || []);
            renderChartTipoPedido(data.pedidos_por_tipo || []);
            renderTablaInsumosCriticos(data.insumos_criticos || []);
            renderTablaMovimientos(data.movimientos_recientes || []);
        })
        .catch(err => {
            console.error('Error cargando dashboard:', err);
        });
}

function mostrarAlertaNuevoPedido(texto) {
    const alertBox = document.getElementById('pedidoAlert');
    const alertText = document.getElementById('pedidoAlertText');
    if (!alertBox || !alertText) return;

    alertText.textContent = texto || 'Se registró un nuevo pedido.';
    alertBox.style.display = 'block';
    if (timeoutOcultarAlerta) clearTimeout(timeoutOcultarAlerta);
    timeoutOcultarAlerta = setTimeout(() => {
        alertBox.style.display = 'none';
    }, 10000);
}

function revisarNuevosPedidos() {
    fetch('/dashboard/api/nuevos-pedidos/')
        .then(response => response.json())
        .then(data => {
            const ultimoId = Number(data.ultimo_pedido_id || 0);
            if (ultimoPedidoConocido === null) {
                ultimoPedidoConocido = ultimoId;
                return;
            }
            if (ultimoId > ultimoPedidoConocido) {
                const cliente = data.cliente_ultimo_pedido ? (' de ' + data.cliente_ultimo_pedido) : '';
                const pendientes = Number(data.pendientes || 0);
                mostrarAlertaNuevoPedido(`Entró un nuevo pedido${cliente}. Pendientes actuales: ${pendientes}.`);
                cargarDashboard();
            }
            ultimoPedidoConocido = Math.max(ultimoPedidoConocido, ultimoId);
        })
        .catch(err => {
            console.error('Error revisando nuevos pedidos:', err);
        });
}

function actualizarKPIs(kpis) {
    document.getElementById('kpiTotalVentas').textContent = formatCurrency(kpis.total_ventas);
    document.getElementById('kpiTotalPedidos').textContent = kpis.total_pedidos;
    document.getElementById('kpiPedidosHoy').textContent = kpis.pedidos_hoy;
    document.getElementById('kpiPendientes').textContent = kpis.pedidos_pendientes;
    document.getElementById('kpiRecibos').textContent = formatCurrency(kpis.recibos_completados);
    document.getElementById('kpiUsuarios').textContent = kpis.total_usuarios;
    document.getElementById('kpiStockBajo').textContent = kpis.insumos_bajo_stock;
    document.getElementById('kpiProductos').textContent = kpis.total_productos;
}

function renderChartVentasDia(data) {
    const ctx = document.getElementById('chartVentasDia');
    if (!ctx) return;

    chartVentasDia = destroyChart(chartVentasDia);
    const theme = chartThemeOptions();

    const totalVentas = data.reduce((sum, d) => sum + Number(d.total || 0), 0);
    if (!data.length || totalVentas === 0) {
        showChartEmpty('chartVentasDia', 'No hay ventas entregadas en este período.');
        return;
    }
    hideChartEmpty('chartVentasDia');

    const labels = data.map(d => {
        const parts = (d.fecha || '').split('-');
        return parts.length === 3 ? parts[2] + '/' + parts[1] : d.fecha;
    });
    const valores = data.map(d => Number(d.total || 0));
    const cantidades = data.map(d => Number(d.cantidad || 0));

    chartVentasDia = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Ventas ($)',
                    data: valores,
                    backgroundColor: 'rgba(220, 38, 38, 0.55)',
                    borderColor: COLORS.red,
                    borderWidth: 1,
                    borderRadius: 6,
                    yAxisID: 'y',
                    order: 2,
                },
                {
                    label: 'Pedidos entregados',
                    data: cantidades,
                    type: 'line',
                    borderColor: COLORS.dark,
                    backgroundColor: 'rgba(17, 17, 17, 0.08)',
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: COLORS.dark,
                    tension: 0.25,
                    yAxisID: 'y1',
                    order: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: theme.text, usePointStyle: true, padding: 12 },
                },
                tooltip: {
                    callbacks: {
                        label(context) {
                            if (context.dataset.label === 'Ventas ($)') {
                                return 'Ventas: ' + formatCurrency(context.raw);
                            }
                            return 'Pedidos: ' + context.raw;
                        },
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    ticks: {
                        color: theme.text,
                        callback(value) { return formatCurrency(value); },
                    },
                    grid: { color: theme.grid },
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: theme.text, stepSize: 1, precision: 0 },
                },
                x: {
                    ticks: { color: theme.text, maxRotation: 45, minRotation: 0 },
                    grid: { display: false },
                },
            },
        },
    });
}

function renderChartPedidosEstado(data) {
    const ctx = document.getElementById('chartPedidosEstado');
    if (!ctx) return;

    chartPedidosEstado = destroyChart(chartPedidosEstado);
    const theme = chartThemeOptions();

    const filtered = data.filter(d => Number(d.cantidad) > 0);
    if (!filtered.length) {
        showChartEmpty('chartPedidosEstado', 'No hay pedidos en el período seleccionado.');
        return;
    }
    hideChartEmpty('chartPedidosEstado');

    const labels = filtered.map(d => ESTADO_LABELS[d.estado_pedido] || d.estado_pedido);
    const valores = filtered.map(d => d.cantidad);
    const bgColors = filtered.map(d => (ESTADO_COLORS[d.estado_pedido] || { bg: COLORS.neutralLight }).bg);
    const borderColors = filtered.map(d => (ESTADO_COLORS[d.estado_pedido] || { border: COLORS.neutral }).border);

    chartPedidosEstado = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: bgColors,
                borderColor: theme.border,
                borderWidth: 2,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '58%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: theme.text, usePointStyle: true, padding: 12, font: { size: 11 } },
                },
            },
        },
    });
}

function renderChartProductosTop(data) {
    const ctx = document.getElementById('chartProductosTop');
    if (!ctx) return;

    chartProductosTop = destroyChart(chartProductosTop);
    const theme = chartThemeOptions();

    if (!data.length) {
        showChartEmpty('chartProductosTop', 'Aún no hay productos vendidos en este período.');
        return;
    }
    hideChartEmpty('chartProductosTop');

    const labels = data.map(d => d.nombre || 'Producto');
    const cantidades = data.map(d => Number(d.total_vendido || 0));
    const ingresos = data.map(d => Number(d.ingresos || 0));

    chartProductosTop = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Unidades vendidas',
                data: cantidades,
                backgroundColor: COLORS.red,
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label(context) {
                            const idx = context.dataIndex;
                            return [
                                'Unidades: ' + context.raw,
                                'Ingresos: ' + formatCurrency(ingresos[idx]),
                            ];
                        },
                    },
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { color: theme.text, stepSize: 1, precision: 0 },
                    grid: { color: theme.grid },
                },
                y: {
                    ticks: { color: theme.text },
                    grid: { display: false },
                },
            },
        },
    });
}

function renderChartTipoPedido(data) {
    const ctx = document.getElementById('chartTipoPedido');
    if (!ctx) return;

    chartTipoPedido = destroyChart(chartTipoPedido);
    const theme = chartThemeOptions();

    const filtered = data.filter(d => Number(d.cantidad) > 0);
    if (!filtered.length) {
        showChartEmpty('chartTipoPedido', 'No hay pedidos por tipo en este período.');
        return;
    }
    hideChartEmpty('chartTipoPedido');

    const labels = filtered.map(d => TIPO_LABELS[d.tipo_pedido] || d.tipo_pedido);
    const valores = filtered.map(d => d.cantidad);
    const palette = [COLORS.red, COLORS.dark, COLORS.info, COLORS.warning];

    chartTipoPedido = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: palette.slice(0, valores.length),
                borderColor: theme.border,
                borderWidth: 2,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: theme.text, usePointStyle: true, padding: 12, font: { size: 11 } },
                },
            },
        },
    });
}

function renderTablaInsumosCriticos(data) {
    const tbody = document.querySelector('#tablaInsumosCriticos tbody');
    if (!tbody) return;

    if (data.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="3">✅ Todos los insumos tienen stock suficiente.</td></tr>';
        return;
    }

    let html = '';
    data.forEach(item => {
        const estadoBadge = item.estado_insumo === 'disponible'
            ? '<span class="se-badge se-badge-warning">Bajo</span>'
            : '<span class="se-badge se-badge-danger">' + item.estado_insumo + '</span>';

        html += '<tr>';
        html += '<td><strong>' + item.nombre_insumo + '</strong></td>';
        html += '<td class="text-center">' + item.stock_actual + ' ' + (item.unidad_medida || '') + '</td>';
        html += '<td class="text-center">' + estadoBadge + '</td>';
        html += '</tr>';
    });

    tbody.innerHTML = html;
}

function renderTablaMovimientos(data) {
    const tbody = document.querySelector('#tablaMovimientos tbody');
    if (!tbody) return;

    if (data.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="4">No hay movimientos recientes.</td></tr>';
        return;
    }

    const tipoLabels = {
        entrada: '<span class="se-badge se-badge-success">Entrada</span>',
        entrada_inicial: '<span class="se-badge se-badge-success">Entrada</span>',
        salida_venta: '<span class="se-badge se-badge-warning">Venta</span>',
        salida_desperdicio: '<span class="se-badge se-badge-danger">Desperdicio</span>',
        ajuste: '<span class="se-badge se-badge-info">Ajuste</span>',
    };

    let html = '';
    data.forEach(item => {
        html += '<tr>';
        html += '<td>' + (tipoLabels[item.tipo_movimiento] || item.tipo_movimiento) + '</td>';
        html += '<td>' + (item.insumo_nombre || '-') + '</td>';
        html += '<td class="text-center"><strong>' + item.cantidad + '</strong></td>';
        html += '<td>' + item.fecha_movimiento + '</td>';
        html += '</tr>';
    });

    tbody.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
    setDefaultDates();
    cargarDashboard();
    revisarNuevosPedidos();
    setInterval(revisarNuevosPedidos, 15000);
});

window.cargarDashboard = cargarDashboard;
window.resetFiltros = resetFiltros;
