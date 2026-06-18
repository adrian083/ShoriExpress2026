/**
 * Shori Express - Smart Search Engine
 * Reusable search/filter system for list tables or card grids.
 *
 * Table mode: pass containerId, tableId (DOM id of <table>), filters.
 * Card mode: pass containerId, targetSelector (e.g. '.se-card-invoice'),
 *            filterIdPrefix (unique string for input ids), filters.
 *
 * Card filter extras:
 *  - text + rowDataKey: match row.dataset[rowDataKey] (e.g. pedidoEstado for data-pedido-estado)
 *  - text + columns: match <td> indices (table mode)
 *  - select + rowDataKey: same as text substring match on dataset value
 *  - date_range + rowDataKey: dataset value should be ISO date (YYYY-MM-DD)
 */

function initSmartSearch(config) {
    const { containerId, tableId, filters, targetSelector, filterIdPrefix } = config;
    const filterIdBase = filterIdPrefix || tableId || 'smartTable';
    const container = document.getElementById(containerId);
    const table = tableId ? document.getElementById(tableId) : null;
    const cardMode = Boolean(targetSelector);

    if (!container) {
        console.warn('SmartSearch: Container not found.', containerId);
        return;
    }
    if (!cardMode && !table) {
        console.warn('SmartSearch: Table not found.', tableId);
        return;
    }

    function rowDatasetValue(row, key) {
        if (!key || !row || !row.dataset) return '';
        return row.dataset[key] || '';
    }

    // Build filter UI
    let html = '<div class="se-search-bar">';

    filters.forEach((filter, idx) => {
        const fId = 'filter_' + filterIdBase + '_' + idx;

        switch (filter.type) {
            case 'text':
                html += '<div class="se-search-field">';
                html += '<label class="se-form-label">' + filter.label + '</label>';
                html += '<input type="text" id="' + fId + '" class="se-form-control se-search-input" placeholder="' + (filter.placeholder || 'Buscar...') + '" data-filter-idx="' + idx + '">';
                html += '</div>';
                break;

            case 'select':
                html += '<div class="se-search-field">';
                html += '<label class="se-form-label">' + filter.label + '</label>';
                html += '<select id="' + fId + '" class="se-form-control se-search-input" data-filter-idx="' + idx + '">';
                html += '<option value="">Todos</option>';
                if (filter.options) {
                    filter.options.forEach(opt => {
                        html += '<option value="' + opt.value + '">' + opt.label + '</option>';
                    });
                }
                html += '</select>';
                html += '</div>';
                break;

            case 'date_range':
                html += '<div class="se-search-field">';
                html += '<label class="se-form-label">' + filter.label + ' (Desde)</label>';
                html += '<input type="date" id="' + fId + '_from" class="se-form-control se-search-input" data-filter-idx="' + idx + '" data-range="from">';
                html += '</div>';
                html += '<div class="se-search-field">';
                html += '<label class="se-form-label">' + filter.label + ' (Hasta)</label>';
                html += '<input type="date" id="' + fId + '_to" class="se-form-control se-search-input" data-filter-idx="' + idx + '" data-range="to">';
                html += '</div>';
                break;

            case 'number_range':
                html += '<div class="se-search-field">';
                html += '<label class="se-form-label">' + filter.label + ' (Mín)</label>';
                html += '<input type="number" step="any" id="' + fId + '_min" class="se-form-control se-search-input" placeholder="Mín" data-filter-idx="' + idx + '" data-range="min">';
                html += '</div>';
                html += '<div class="se-search-field">';
                html += '<label class="se-form-label">' + filter.label + ' (Máx)</label>';
                html += '<input type="number" step="any" id="' + fId + '_max" class="se-form-control se-search-input" placeholder="Máx" data-filter-idx="' + idx + '" data-range="max">';
                html += '</div>';
                break;
        }
    });

    html += '<div class="se-search-field se-search-actions">';
    html += '<button type="button" class="se-btn se-btn-outline se-btn-sm" id="clearFilters_' + filterIdBase + '">Limpiar</button>';
    html += '</div>';
    html += '</div>';

    html += '<div class="se-search-count" id="searchCount_' + filterIdBase + '"></div>';

    container.innerHTML = html;

    let rows = [];
    let emptyRow = null;
    if (cardMode) {
        rows = Array.from(document.querySelectorAll(targetSelector));
    } else {
        const tbody = table.querySelector('tbody');
        rows = tbody ? Array.from(tbody.querySelectorAll('tr:not(.empty-row)')) : [];
        emptyRow = tbody ? tbody.querySelector('tr.empty-row') : null;
    }

    function applyFilters() {
        let visibleCount = 0;

        rows.forEach(row => {
            const cells = cardMode ? [] : Array.from(row.querySelectorAll('td'));
            let visible = true;

            filters.forEach((filter, idx) => {
                const fId = 'filter_' + filterIdBase + '_' + idx;

                switch (filter.type) {
                    case 'text': {
                        const input = document.getElementById(fId);
                        if (!input) break;
                        const query = input.value.toLowerCase().trim();
                        if (!query) break;

                        if (cardMode && filter.selector) {
                            const el = row.querySelector(filter.selector);
                            const t = (el && el.textContent || '').toLowerCase();
                            if (!t.includes(query)) visible = false;
                            break;
                        }

                        if (cardMode && filter.rowDataKey) {
                            const raw = rowDatasetValue(row, filter.rowDataKey).toLowerCase();
                            if (!raw.includes(query)) visible = false;
                            break;
                        }

                        const colIndices = filter.columns || [];
                        let found = false;

                        if (colIndices.length === 0) {
                            found = cells.some(cell => cell.textContent.toLowerCase().includes(query));
                        } else {
                            found = colIndices.some(ci => {
                                const cell = cells[ci];
                                return cell && cell.textContent.toLowerCase().includes(query);
                            });
                        }

                        if (!found) visible = false;
                        break;
                    }

                    case 'select': {
                        const select = document.getElementById(fId);
                        if (!select) break;
                        const val = select.value.toLowerCase().trim();
                        if (!val) break;

                        if (cardMode && filter.rowDataKey) {
                            const raw = rowDatasetValue(row, filter.rowDataKey).toLowerCase();
                            if (!raw.includes(val)) visible = false;
                            break;
                        }

                        const colIdx = filter.column;
                        const cell = cells[colIdx];
                        if (!cell) { visible = false; break; }

                        const cellText = cell.textContent.toLowerCase().trim();
                        if (!cellText.includes(val)) visible = false;
                        break;
                    }

                    case 'date_range': {
                        const fromInput = document.getElementById(fId + '_from');
                        const toInput = document.getElementById(fId + '_to');
                        if (!fromInput || !toInput) break;

                        const fromVal = fromInput.value;
                        const toVal = toInput.value;
                        if (!fromVal && !toVal) break;

                        let cellText = '';
                        if (cardMode && filter.rowDataKey) {
                            cellText = (rowDatasetValue(row, filter.rowDataKey) || '').trim();
                        } else {
                            const colIdx = filter.column;
                            const cell = cells[colIdx];
                            if (!cell) { visible = false; break; }
                            cellText = cell.textContent.trim();
                        }

                        let cellDate = extractDate(cellText);
                        if (!cellDate) { visible = false; break; }

                        if (fromVal && cellDate < fromVal) visible = false;
                        if (toVal && cellDate > toVal) visible = false;
                        break;
                    }

                    case 'number_range': {
                        const minInput = document.getElementById(fId + '_min');
                        const maxInput = document.getElementById(fId + '_max');
                        if (!minInput || !maxInput) break;

                        const minVal = minInput.value;
                        const maxVal = maxInput.value;
                        if (!minVal && !maxVal) break;

                        let num;
                        if (cardMode && filter.rowDataKey) {
                            num = parseFloat(rowDatasetValue(row, filter.rowDataKey));
                        } else {
                            const colIdx = filter.column;
                            const cell = cells[colIdx];
                            if (!cell) { visible = false; break; }
                            num = parseNumber(cell.textContent);
                        }
                        if (isNaN(num)) { visible = false; break; }

                        if (minVal && num < parseFloat(minVal)) visible = false;
                        if (maxVal && num > parseFloat(maxVal)) visible = false;
                        break;
                    }
                }
            });

            row.style.display = visible ? '' : 'none';
            if (visible) visibleCount++;
        });

        if (!cardMode && emptyRow) {
            if (visibleCount === 0 && rows.length > 0) {
                emptyRow.style.display = '';
                const td = emptyRow.querySelector('td');
                if (td) td.textContent = 'No se encontraron resultados con los filtros aplicados.';
            } else if (rows.length === 0) {
                emptyRow.style.display = '';
            } else {
                emptyRow.style.display = 'none';
            }
        }

        const countEl = document.getElementById('searchCount_' + filterIdBase);
        if (countEl) {
            if (rows.length > 0) {
                countEl.textContent = 'Mostrando ' + visibleCount + ' de ' + rows.length + ' registros';
            } else {
                countEl.textContent = '';
            }
        }
    }

    function extractDate(text) {
        let match = text.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (match) return match[0];

        match = text.match(/(\d{2})\/(\d{2})\/(\d{4})/);
        if (match) return match[3] + '-' + match[2] + '-' + match[1];

        const parsed = new Date(text);
        if (!isNaN(parsed.getTime())) {
            return parsed.toISOString().split('T')[0];
        }

        return null;
    }

    function parseNumber(text) {
        const cleaned = text.replace(/[^0-9.\-]/g, '');
        return parseFloat(cleaned);
    }

    const inputs = container.querySelectorAll('.se-search-input');
    inputs.forEach(input => {
        const eventType = (input.tagName === 'SELECT' || input.type === 'date') ? 'change' : 'input';
        input.addEventListener(eventType, applyFilters);
        if (input.type === 'date') {
            input.addEventListener('input', applyFilters);
        }
    });

    const clearBtn = document.getElementById('clearFilters_' + filterIdBase);
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            inputs.forEach(input => {
                input.value = '';
            });
            applyFilters();
        });
    }

    applyFilters();
}
