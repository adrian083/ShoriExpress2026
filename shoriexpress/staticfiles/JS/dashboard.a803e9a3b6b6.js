let chartVentasDia = null;
let chartPedidosEstado = null;
let chartProductosTop = null;
let chartTipoPedido = null;
let ultimoPedidoConocido = null;
let timeoutOcultarAlerta = null;

const COLORS = {
    red: '#DC2626',
    redLight: 'rgba(220, 38, 38, 0.2)',
    dark: '#111111',
    darkLight: 'rgba(17, 17, 17, 0.1)',
    success: '#16A34A',
    successLight: 'rgba(22, 163, 74, 0.2)',
    warning: '#D97706',
    warningLight: 'rgba(217, 119, 6, 0.2)',
    info: '#2563EB',
    infoLight: 'rgba(37, 99, 235, 0.2)',
    neutral: '#6B7280',
    neutralLight: 'rgba(107, 114, 128, 0.2)',
};

const ESTADO_COLORS = {
    'pendiente': { bg: COLORS.warningLight, border: COLORS.warning },
    'preparacion': { bg: COLORS.infoLight, border: COLORS.info },
    'listo': { bg: COLORS.successLight, border: COLORS.success },
    'entregado': { bg: COLORS.successLight, border: COLORS.success },
    'cancelado': { bg: COLORS.redLight, border: COLORS.red },
};

function formatCurrency(value) {
    return '$' + Number(value).toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
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
    if (fechaInicio) url += 'fecha_inicio=' + fechaInicio + '&';
    if (fechaFin) url += 'fecha_fin=' + fechaFin;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Respuesta no OK en dashboard-data: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            actualizarKPIs(data.kpis);
            renderChartVentasDia(data.ventas_por_dia);
            renderChartPedidosEstado(data.pedidos_por_estado);
            renderChartProductosTop(data.productos_top);
            renderChartTipoPedido(data.pedidos_por_tipo);
            renderTablaInsumosCriticos(data.insumos_criticos);
            renderTablaMovimientos(data.movimientos_recientes);
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

    if (chartVentasDia) chartVentasDia.destroy();

    const labels = data.map(d => {
        const parts = d.fecha.split('-');
        return parts[2] + '/' + parts[1];
    });
    const valores = data.map(d => d.total);
    const cantidades = data.map(d => d.cantidad);

    chartVentasDia = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Ventas ($)',
                    data: valores,
                    backgroundColor: COLORS.redLight,
                    borderColor: COLORS.red,
                    borderWidth: 2,
                    borderRadius: 6,
                    yAxisID: 'y',
                },
                {
                    label: 'Pedidos',
                    data: cantidades,
                    type: 'line',
                    borderColor: COLORS.dark,
                    backgroundColor: COLORS.darkLight,
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: COLORS.dark,
                    tension: 0.3,
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label === 'Ventas ($)') {
                                return 'Ventas: ' + formatCurrency(context.raw);
                            }
                            return 'Pedidos: ' + context.raw;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    ticks: {
                        callback: function(value) { return formatCurrency(value); }
                    },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { stepSize: 1 }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function renderChartPedidosEstado(data) {
    const ctx = document.getElementById('chartPedidosEstado');
    if (!ctx) return;

    if (chartPedidosEstado) chartPedidosEstado.destroy();

    const labels = data.map(d => d.estado_pedido.charAt(0).toUpperCase() + d.estado_pedido.slice(1));
    const valores = data.map(d => d.cantidad);
    const borderColors = data.map(d => (ESTADO_COLORS[d.estado_pedido] || { border: COLORS.neutral }).border);

    chartPedidosEstado = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: borderColors,
                borderColor: '#fff',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, padding: 16, font: { size: 12 } }
                }
            }
        }
    });
}

function renderChartProductosTop(data) {
    const ctx = document.getElementById('chartProductosTop');
    if (!ctx) return;

    if (chartProductosTop) chartProductosTop.destroy();

    if (data.length === 0) {
        chartProductosTop = new Chart(ctx, {
            type: 'bar',
            data: { labels: ['Sin datos'], datasets: [{ data: [0], backgroundColor: COLORS.neutralLight }] },
            options: { responsive: true, maintainAspectRatio: false }
        });
        return;
    }

    const labels = data.map(d => d.nombre);
    const cantidades = data.map(d => d.total_vendido);
    const ingresos = data.map(d => d.ingresos);

    chartProductosTop = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Unidades Vendidas',
                    data: cantidades,
                    backgroundColor: COLORS.red,
                    borderRadius: 6,
                },
                {
                    label: 'Ingresos ($)',
                    data: ingresos,
                    backgroundColor: COLORS.dark,
                    borderRadius: 6,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label.includes('Ingresos')) {
                                return 'Ingresos: ' + formatCurrency(context.raw);
                            }
                            return 'Vendidos: ' + context.raw;
                        }
                    }
                }
            },
            scales: {
                x: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                y: { grid: { display: false } }
            }
        }
    });
}

function renderChartTipoPedido(data) {
    const ctx = document.getElementById('chartTipoPedido');
    if (!ctx) return;

    if (chartTipoPedido) chartTipoPedido.destroy();

    const labels = data.map(d => d.tipo_pedido);
    const valores = data.map(d => d.cantidad);

    chartTipoPedido = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: [COLORS.red, COLORS.dark, COLORS.info, COLORS.warning],
                borderColor: '#fff',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, padding: 16, font: { size: 12 } }
                }
            }
        }
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
        'entrada': '<span class="se-badge se-badge-success">Entrada</span>',
        'salida_venta': '<span class="se-badge se-badge-warning">Venta</span>',
        'salida_desperdicio': '<span class="se-badge se-badge-danger">Desperdicio</span>',
        'ajuste': '<span class="se-badge se-badge-info">Ajuste</span>',
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