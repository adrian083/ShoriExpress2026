# FORMATO CASOS DE PRUEBA
## Módulo: Auditoría de Detalles de Pedido

---

## CASO DE PRUEBA: FIL-001

### Información General

| Aspecto | Descripción |
|---------|-------------|
| **ID Caso** | FIL-001 |
| **Título** | Filtrar detalles de pedido por estado del pedido y disponibilidad del producto |
| **Módulo** | `detalle_pedido` |
| **Versión** | 1.0 |
| **Autor** | Equipo QA |
| **Fecha Creación** | 2026-05-13 |

---

## DESCRIPCIÓN

**Narrativa:**
```
Como administrador, quiero filtrar la lista de detalles de pedido por estado del 
pedido y disponibilidad del producto para auditar líneas específicas.
```

**Objetivo:**
Validar que el sistema permite al usuario administrador filtrar y visualizar detalles 
de pedidos según criterios de:
- Estado del pedido (Pendiente, En Preparación, Listo para Entrega, Entregado, Cancelado)
- Disponibilidad del producto (Disponible, No Disponible)

---

## CONDICIONES DE EJECUCIÓN

| Condición | Requisito |
|-----------|-----------|
| **Ambiente** | Servidor de desarrollo/staging |
| **Base de Datos** | SQLite con datos de prueba (mínimo 10 detalles de pedido) |
| **Usuario** | Administrador autenticado con permisos super_admin_required |
| **Datos Previos** | Existen pedidos con diferentes estados y productos con distinta disponibilidad |
| **Navegador** | Chrome 120+, Firefox 121+, Edge 120+ |
| **Sesión** | Sesión activa con variables `usuario_id` y permisos administrativos |

---

## PRERREQUISITOS (Setup)

Antes de ejecutar las pruebas, asegurar que existan en la base de datos:

### Datos de Prueba Requeridos

#### Usuarios
```python
# Usuario Administrador
usuario_admin = Usuario.objects.create(
    primer_nombre="Carlos",
    apellido="García",
    correo_electronico="admin@shoriexpress.test",
    es_administrador=True,
    es_vendedor=True
)
```

#### Productos
```python
# Productos con diferentes disponibilidades
Producto.objects.create(
    nombre_producto="Sándwich Clásico",
    precio_venta=8.50,
    esta_disponible=True,
    esta_habilitado=True
)

Producto.objects.create(
    nombre_producto="Empanada Premium",
    precio_venta=6.00,
    esta_disponible=False,
    esta_habilitado=False
)

Producto.objects.create(
    nombre_producto="Bebida Refrescante",
    precio_venta=2.50,
    esta_disponible=True,
    esta_habilitado=True
)
```

#### Pedidos (con diferentes estados)
```python
# Pedido 1: Estado Pendiente
pedido_pendiente = Pedido.objects.create(
    usuario=usuario_admin,
    tipo_pedido='local',
    estado_pedido='pendiente',
    total_pedido=11.00
)

# Pedido 2: Estado En Preparación
pedido_preparacion = Pedido.objects.create(
    usuario=usuario_admin,
    tipo_pedido='llevar',
    estado_pedido='preparacion',
    total_pedido=14.50
)

# Pedido 3: Estado Listo
pedido_listo = Pedido.objects.create(
    usuario=usuario_admin,
    tipo_pedido='domicilio',
    estado_pedido='listo',
    total_pedido=20.00
)

# Pedido 4: Estado Entregado
pedido_entregado = Pedido.objects.create(
    usuario=usuario_admin,
    tipo_pedido='local',
    estado_pedido='entregado',
    total_pedido=18.50
)

# Pedido 5: Estado Cancelado
pedido_cancelado = Pedido.objects.create(
    usuario=usuario_admin,
    tipo_pedido='llevar',
    estado_pedido='cancelado',
    total_pedido=9.00
)
```

#### Detalles de Pedido (Vinculaciones)
```python
# Detalle 1: Producto disponible, Pedido pendiente
DetallePedido.objects.create(
    pedido=pedido_pendiente,
    producto=producto_sandwich,
    cantidad=1,
    precio_unitario_momento=8.50,
    stock_remanente_post_venta=45
)

# Detalle 2: Producto NO disponible, Pedido pendiente
DetallePedido.objects.create(
    pedido=pedido_pendiente,
    producto=producto_empanada,
    cantidad=1,
    precio_unitario_momento=6.00,
    stock_remanente_post_venta=0
)

# Detalle 3: Producto disponible, Pedido en preparación
DetallePedido.objects.create(
    pedido=pedido_preparacion,
    producto=producto_sandwich,
    cantidad=2,
    precio_unitario_momento=8.50,
    stock_remanente_post_venta=43
)

# Detalle 4: Producto disponible, Pedido listo
DetallePedido.objects.create(
    pedido=pedido_listo,
    producto=producto_bebida,
    cantidad=3,
    precio_unitario_momento=2.50,
    stock_remanente_post_venta=47
)

# Detalle 5: Producto NO disponible, Pedido entregado
DetallePedido.objects.create(
    pedido=pedido_entregado,
    producto=producto_empanada,
    cantidad=2,
    precio_unitario_momento=6.00,
    stock_remanente_post_venta=0
)

# Detalle 6: Producto disponible, Pedido cancelado
DetallePedido.objects.create(
    pedido=pedido_cancelado,
    producto=producto_sandwich,
    cantidad=1,
    precio_unitario_momento=8.50,
    stock_remanente_post_venta=46
)
```

---

## DISEÑO DE CASOS DE PRUEBA

### Escenario 1: Filtrar por Estado del Pedido - "Pendiente"

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.1 |
| **Descripción** | El administrador filtra detalles de pedidos en estado "Pendiente" |
| **Datos Entrada** | Filtro: `estado_pedido = 'pendiente'` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Estado del Pedido" <br> 3. Elegir opción "Pendiente" <br> 4. Aplicar filtro |
| **Resultado Esperado** | ✅ Se muestran solo detalles vinculados a pedidos con estado "Pendiente" (2 registros: Sándwich y Empanada) |
| **Criterios de Aceptación** | • La lista contiene solo 2 detalles <br> • Ambos detalles están asociados a `pedido.estado_pedido = 'pendiente'` <br> • Los datos mostrados son: cantidad, producto, precio unitario, pedido ID |
| **Observaciones** | N/A |

---

### Escenario 2: Filtrar por Estado del Pedido - "En Preparación"

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.2 |
| **Descripción** | El administrador filtra detalles de pedidos en estado "En Preparación" |
| **Datos Entrada** | Filtro: `estado_pedido = 'preparacion'` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Estado del Pedido" <br> 3. Elegir opción "En Preparación" <br> 4. Aplicar filtro |
| **Resultado Esperado** | ✅ Se muestran solo detalles vinculados a pedidos en estado "En Preparación" (1 registro: 2x Sándwich) |
| **Criterios de Aceptación** | • La lista contiene solo 1 detalle <br> • El detalle está asociado a `pedido.estado_pedido = 'preparacion'` <br> • Muestra cantidad=2 del producto Sándwich Clásico |
| **Observaciones** | N/A |

---

### Escenario 3: Filtrar por Disponibilidad del Producto - "Disponible"

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.3 |
| **Descripción** | El administrador filtra detalles con productos disponibles |
| **Datos Entrada** | Filtro: `producto.esta_disponible = True` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Disponibilidad del Producto" <br> 3. Elegir opción "Disponible" <br> 4. Aplicar filtro |
| **Resultado Esperado** | ✅ Se muestran solo detalles con productos marcados como disponibles (4 registros) |
| **Criterios de Aceptación** | • La lista contiene 4 detalles <br> • Todos tienen `producto.esta_disponible = True` <br> • Los productos mostrados son: Sándwich (3x), Bebida (3x) |
| **Observaciones** | Se excluyen productos marcados como no disponibles |

---

### Escenario 4: Filtrar por Disponibilidad del Producto - "No Disponible"

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.4 |
| **Descripción** | El administrador filtra detalles con productos no disponibles |
| **Datos Entrada** | Filtro: `producto.esta_disponible = False` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Disponibilidad del Producto" <br> 3. Elegir opción "No Disponible" <br> 4. Aplicar filtro |
| **Resultado Esperado** | ✅ Se muestran solo detalles con productos marcados como no disponibles (2 registros) |
| **Criterios de Aceptación** | • La lista contiene 2 detalles <br> • Todos tienen `producto.esta_disponible = False` <br> • El producto mostrado es: Empanada Premium (2 registros en diferentes pedidos) |
| **Observaciones** | Útil para auditar líneas que contenían productos fuera del menú |

---

### Escenario 5: Filtrar por Combinación de Criterios

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.5 |
| **Descripción** | El administrador filtra detalles que cumplan ambos criterios: Estado "Listo" Y Producto "Disponible" |
| **Datos Entrada** | Filtros: `estado_pedido = 'listo' AND producto.esta_disponible = True` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Estado del Pedido" → "Listo" <br> 3. Aplicar primer filtro <br> 4. Seleccionar filtro "Disponibilidad del Producto" → "Disponible" <br> 5. Aplicar segundo filtro (o aplicar ambos simultáneamente si la UI lo permite) |
| **Resultado Esperado** | ✅ Se muestran detalles en pedidos "Listo" con productos disponibles (1 registro: 3x Bebida) |
| **Criterios de Aceptación** | • La lista contiene exactamente 1 detalle <br> • El detalle tiene: `pedido.estado_pedido = 'listo' AND producto.esta_disponible = True` <br> • Muestra el producto Bebida Refrescante con cantidad=3 |
| **Observaciones** | Comprueba la intersección lógica de filtros |

---

### Escenario 6: Filtrar por Estado "Entregado"

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.6 |
| **Descripción** | El administrador filtra detalles de pedidos entregados para auditoría de histórico |
| **Datos Entrada** | Filtro: `estado_pedido = 'entregado'` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Estado del Pedido" <br> 3. Elegir opción "Entregado" <br> 4. Aplicar filtro |
| **Resultado Esperado** | ✅ Se muestran solo detalles vinculados a pedidos entregados (1 registro: 2x Empanada) |
| **Criterios de Aceptación** | • La lista contiene 1 detalle <br> • El detalle está asociado a `pedido.estado_pedido = 'entregado'` <br> • Se pueden ver campos de auditoría: `stock_remanente_post_venta`, `precio_unitario_momento` |
| **Observaciones** | Importante para trazabilidad y auditoría de stock post-venta |

---

### Escenario 7: Filtrar por Estado "Cancelado"

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.7 |
| **Descripción** | El administrador filtra detalles de pedidos cancelados |
| **Datos Entrada** | Filtro: `estado_pedido = 'cancelado'` |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Seleccionar filtro "Estado del Pedido" <br> 3. Elegir opción "Cancelado" <br> 4. Aplicar filtro |
| **Resultado Esperado** | ✅ Se muestran solo detalles vinculados a pedidos cancelados (1 registro: 1x Sándwich) |
| **Criterios de Aceptación** | • La lista contiene 1 detalle <br> • El detalle está asociado a `pedido.estado_pedido = 'cancelado'` <br> • Se visualiza claramente que el pedido fue cancelado |
| **Observaciones** | N/A |

---

### Escenario 8: Limpiar Filtros (Reset)

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.8 |
| **Descripción** | El administrador limpia los filtros aplicados y ve todos los detalles nuevamente |
| **Datos Entrada** | Botón/acción: "Limpiar Filtros" o "Mostrar Todos" |
| **Acciones** | 1. Navegar a `/detalle_pedido/` con filtros aplicados <br> 2. Hacer clic en botón "Limpiar Filtros" o "Reset" <br> 3. Verificar que se muestren todos los detalles |
| **Resultado Esperado** | ✅ Se muestran los 6 detalles de pedido sin restricciones (estado de vista inicial) |
| **Criterios de Aceptación** | • La lista contiene 6 detalles <br> • No hay filtros activos <br> • Los datos se ordenan por `fecha_pedido` descendente (más recientes primero) |
| **Observaciones** | Verifica que el sistema no mantiene filtros previos |

---

### Escenario 9: Validación de Permisos - Usuario sin Admin

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.9 |
| **Descripción** | Un usuario sin permisos de administrador intenta acceder a la lista de detalles filtrados |
| **Datos Entrada** | Usuario: vendedor o cliente (no admin) |
| **Acciones** | 1. Iniciar sesión como usuario no-administrador <br> 2. Intentar acceder a `/detalle_pedido/` <br> 3. Observar la respuesta del sistema |
| **Resultado Esperado** | ❌ Se redirige a una página de error (403 Forbidden o acceso denegado) |
| **Criterios de Aceptación** | • El decorador `@super_admin_required` detiene el acceso <br> • Se muestra mensaje de error apropiado <br> • No se carga la lista de detalles <br> • Se registra el intento no autorizado (en logs) |
| **Observaciones** | Seguridad: la funcionalidad es solo para administradores |

---

### Escenario 10: Rendimiento - Carga con Muchos Registros

| Aspecto | Detalle |
|---------|---------|
| **Código** | FIL-001.10 |
| **Descripción** | Validar que los filtros funcionan eficientemente con 1000+ detalles de pedido |
| **Datos Entrada** | Base de datos con 1000 detalles de pedido en diferentes estados |
| **Acciones** | 1. Navegar a `/detalle_pedido/` <br> 2. Aplicar filtro por estado "Pendiente" <br> 3. Medir tiempo de respuesta <br> 4. Verificar que se usa `select_related()` para optimizar queries |
| **Resultado Esperado** | ✅ La página carga en menos de 2 segundos <br> ✅ Se usa `select_related()` para evitar N+1 queries |
| **Criterios de Aceptación** | • Tiempo de respuesta < 2 segundos <br> • En `django.db.connection.queries`: máximo 3-4 queries (no una por registro) <br> • La consulta SQL incluye JOIN con `pedido` y `producto` |
| **Observaciones** | Revisar código en `vista_lista_detalles()`: ya tiene `select_related()` implementado |

---

## PRIORIDAD

| Nivel | Justificación |
|-------|---------------|
| **ALTA** | Funcionalidad crítica para auditoría y control administrativo del sistema. Es requisito funcional del negocio. |

---

## IMPACTO Y OBSERVACIONES

### Observaciones Técnicas

1. **Implementación Requerida en `detalle_pedido/views.py`:**
   ```python
   @super_admin_required
   def lista_detalles(request):
       detalles = DetallePedido.objects.select_related(
           'pedido', 
           'pedido__usuario',
           'producto'
       )
       
       # NUEVO: Filtros por parámetros GET
       estado_pedido = request.GET.get('estado_pedido')
       disponibilidad = request.GET.get('disponibilidad')
       
       if estado_pedido and estado_pedido in dict(Pedido.ESTADOS_PEDIDO):
           detalles = detalles.filter(pedido__estado_pedido=estado_pedido)
       
       if disponibilidad:
           if disponibilidad == 'disponible':
               detalles = detalles.filter(producto__esta_disponible=True)
           elif disponibilidad == 'no_disponible':
               detalles = detalles.filter(producto__esta_disponible=False)
       
       detalles = detalles.order_by('-pedido__fecha_pedido')
       
       context = {
           'detalles': detalles,
           'estados_disponibles': Pedido.ESTADOS_PEDIDO,
           'filtro_estado': estado_pedido,
           'filtro_disponibilidad': disponibilidad,
       }
       return render(request, 'detalle_pedido/lista_detalles_cards.html', context)
   ```

2. **Plantilla HTML requerida:**
   - Crear controles de filtro en `detalle_pedido/lista_detalles_cards.html`
   - Usar `<select>` o botones para seleccionar filtros
   - Incluir botón "Limpiar Filtros" para resetear

3. **Validaciones:**
   - El valor de `estado_pedido` debe existir en `Pedido.ESTADOS_PEDIDO`
   - El valor de `disponibilidad` debe ser 'disponible' o 'no_disponible'
   - Se debe usar `select_related()` para evitar queries N+1

4. **Auditoría:**
   - Los campos `stock_remanente_post_venta` y `precio_unitario_momento` son críticos para auditoría
   - Se recomienda mostrar estos campos en la vista filtrada

---

## VERIFICACIÓN (Checklist)

- [ ] Ambiente de prueba configurado con datos de prueba
- [ ] Usuario administrador autenticado
- [ ] Funcionalidad de filtros implementada en backend
- [ ] UI de filtros visible y funcional
- [ ] Validación de permisos (@super_admin_required) activa
- [ ] Queries optimizadas con select_related()
- [ ] Pruebas unitarias para lógica de filtrado
- [ ] Pruebas de UI/E2E para interacción con filtros
- [ ] Documentación de filtros en template
- [ ] Pruebas de seguridad (intento de acceso sin permisos)
- [ ] Pruebas de rendimiento con 1000+ registros
- [ ] Log de auditoría registra acceso administrativo a detalles

---

## REFERENCIAS

- **Modelo DetallePedido:** [detalle_pedido/models.py](../detalle_pedido/models.py)
- **Vista Lista Detalles:** [detalle_pedido/views.py](../detalle_pedido/views.py)
- **Modelo Pedido:** [pedido/models.py](../pedido/models.py)
- **Modelo Producto:** [producto/models.py](../producto/models.py)
- **URLs:** [detalle_pedido/urls.py](../detalle_pedido/urls.py)
- **Template:** `detalle_pedido/lista_detalles_cards.html`

---

## FIRMA DE APROBACIÓN

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Tester QA | _____________ | 2026-05-13 | _____ |
| Desarrollador | _____________ | _____________ | _____ |
| Product Owner | _____________ | _____________ | _____ |
| Jefe de Proyecto | _____________ | _____________ | _____ |

---

**Estado del Documento:** Listo para Ejecución  
**Versión:** 1.0  
**Última Actualización:** 2026-05-13
