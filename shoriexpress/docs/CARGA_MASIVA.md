# Carga masiva (CSV)

Ruta: `Dashboard > Carga masiva`.

## Formatos

### Inventario (insumos)
Archivo: `static/docs/ejemplos/carga_inventario_ejemplo.csv`

Columnas requeridas:
- `nombre_insumo`
- `categoria_insumo`
- `unidad_medida`
- `stock_minimo`
- `precio_compra_referencia`
- `iva_porcentaje`
- `estado_insumo`

Opcionales:
- `stock_actual`
- `stock_maximo`

Regla: si existe un insumo con el mismo `nombre_insumo`, se **actualiza**; si no, se **crea**.

### Productos (menú)
Archivo: `static/docs/ejemplos/carga_productos_ejemplo.csv`
Archivo grande (20+): `static/docs/ejemplos/carga_productos_20_ejemplo.csv`

Columnas requeridas:
- `nombre_producto`
- `descripcion_producto`
- `precio_venta`
- `es_combo` (0/1, true/false, si/no)
- `esta_disponible` (0/1, true/false, si/no)

Opcionales:
- `imagen_catalogo` (ruta relativa bajo `static/`, ej: `productos/perro.jpg`)
- `registro_movimiento_inicial`

Regla: si existe un producto con el mismo `nombre_producto` (ignorando mayúsculas/minúsculas), se **actualiza**; si no, se **crea**.
Si el CSV trae nombres repetidos, esas filas se reportan como error para evitar duplicados.

## Nota
- Usa CSV en **UTF-8**.
- Los decimales pueden venir con `.` o `,`.
