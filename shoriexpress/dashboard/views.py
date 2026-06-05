import json
import csv
import io
import os
import shutil
import subprocess
from pathlib import Path
from django.db import transaction
from datetime import datetime, timedelta
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import TruncDate, TruncMonth, Coalesce
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from cuentas.views import admin_shori_required, super_admin_required

from pedido.models import Pedido
from detalle_pedido.models import DetallePedido
from producto.models import Producto
from inventario.models import Inventario
from recibo.models import Recibo
from usuario.models import Usuario
from movimiento_inventario.models import MovimientoInventario


@admin_shori_required
@require_GET
def dashboard_data_api(request):
    """API endpoint that returns all dashboard statistics as JSON.
    Supports date filtering via GET params: fecha_inicio, fecha_fin
    """
    fecha_inicio_str = request.GET.get('fecha_inicio', '')
    fecha_fin_str = request.GET.get('fecha_fin', '')

    now = timezone.now()

    # Default: last 30 days
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            fecha_inicio = timezone.make_aware(fecha_inicio)
        except ValueError:
            fecha_inicio = now - timedelta(days=30)
    else:
        fecha_inicio = now - timedelta(days=30)

    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            fecha_fin = timezone.make_aware(fecha_fin.replace(hour=23, minute=59, second=59))
        except ValueError:
            fecha_fin = now
    else:
        fecha_fin = now

    # ── KPI Cards ──
    pedidos_periodo = Pedido.objects.filter(fecha_pedido__range=[fecha_inicio, fecha_fin])
    total_ventas = pedidos_periodo.filter(
        estado_pedido='entregado'
    ).aggregate(total=Coalesce(Sum('total_pedido'), 0, output_field=DecimalField()))['total']

    total_pedidos = pedidos_periodo.count()

    pedidos_hoy = Pedido.objects.filter(
        fecha_pedido__date=now.date()
    ).count()

    pedidos_pendientes = Pedido.objects.filter(estado_pedido='pendiente').count()

    # Recibos - model has total_pagado but no estado_pago, sum all
    recibos_completados = Recibo.objects.filter(
        fecha_emision__range=[fecha_inicio, fecha_fin]
    ).aggregate(total=Coalesce(Sum('total_pagado'), 0, output_field=DecimalField()))['total']

    total_usuarios = Usuario.objects.filter(estado='activo').count()

    # Insumos con stock bajo
    insumos_bajo_stock = Inventario.objects.filter(stock_actual__lte=F('stock_minimo')).count()

    total_productos = Producto.objects.count()

    # ── Pedidos por Estado ──
    pedidos_por_estado = list(
        Pedido.objects.values('estado_pedido').annotate(
            cantidad=Count('id')
        ).order_by('estado_pedido')
    )

    # ── Ventas por día (últimos 30 días) ──
    ventas_por_dia = list(
        Pedido.objects.filter(
            estado_pedido='entregado',
            fecha_pedido__range=[fecha_inicio, fecha_fin]
        ).annotate(
            fecha=TruncDate('fecha_pedido')
        ).values('fecha').annotate(
            total=Sum('total_pedido'),
            cantidad=Count('id')
        ).order_by('fecha')
    )
    for item in ventas_por_dia:
        item['fecha'] = item['fecha'].strftime('%Y-%m-%d') if item['fecha'] else ''
        item['total'] = float(item['total']) if item['total'] else 0

    # ── Productos más vendidos (Top 5) ──
    productos_top = list(
        DetallePedido.objects.filter(
            pedido__fecha_pedido__range=[fecha_inicio, fecha_fin],
            pedido__estado_pedido='entregado'
        ).values(
            nombre=F('producto__nombre_producto')
        ).annotate(
            total_vendido=Sum('cantidad'),
            ingresos=Sum(F('cantidad') * F('precio_unitario_momento'), output_field=DecimalField())
        ).order_by('-total_vendido')[:5]
    )
    for item in productos_top:
        item['ingresos'] = float(item['ingresos']) if item['ingresos'] else 0

    # ── Insumos críticos (stock bajo) ──
    insumos_criticos = list(
        Inventario.objects.filter(
            stock_actual__lte=F('stock_minimo')
        ).values(
            'nombre_insumo', 'stock_actual', 'unidad_medida', 'estado_insumo'
        ).order_by('stock_actual')[:8]
    )
    for item in insumos_criticos:
        item['stock_actual'] = float(item['stock_actual'])

    # ── Tipo de pedido distribución ──
    pedidos_por_tipo = list(
        pedidos_periodo.values('tipo_pedido').annotate(
            cantidad=Count('id')
        ).order_by('tipo_pedido')
    )

    # ── Movimientos recientes ──
    movimientos_recientes = list(
        MovimientoInventario.objects.select_related('insumo', 'usuario').order_by(
            '-fecha_movimiento'
        )[:5].values(
            'tipo_movimiento', 'cantidad', 'fecha_movimiento',
            insumo_nombre=F('insumo__nombre_insumo'),
            usuario_nombre=F('usuario__primer_nombre')
        )
    )
    for item in movimientos_recientes:
        item['cantidad'] = float(item['cantidad'])
        item['fecha_movimiento'] = item['fecha_movimiento'].strftime('%Y-%m-%d %H:%M') if item['fecha_movimiento'] else ''

    data = {
        'kpis': {
            'total_ventas': float(total_ventas),
            'total_pedidos': total_pedidos,
            'pedidos_hoy': pedidos_hoy,
            'pedidos_pendientes': pedidos_pendientes,
            'recibos_completados': float(recibos_completados),
            'total_usuarios': total_usuarios,
            'insumos_bajo_stock': insumos_bajo_stock,
            'total_productos': total_productos,
        },
        'pedidos_por_estado': pedidos_por_estado,
        'ventas_por_dia': ventas_por_dia,
        'productos_top': productos_top,
        'insumos_criticos': insumos_criticos,
        'pedidos_por_tipo': pedidos_por_tipo,
        'movimientos_recientes': movimientos_recientes,
        'filtros': {
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        }
    }

    return JsonResponse(data, safe=False)


def _to_decimal(val, default=None):
    from decimal import Decimal, InvalidOperation

    if val is None:
        return default
    s = str(val).strip()
    if s == "":
        return default
    s = s.replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return default


def _nombre_normalizado(val):
    return " ".join((val or "").strip().lower().split())


@admin_shori_required
@require_http_methods(["GET", "POST"])
def carga_masiva(request):
    
    resumen = None

    if request.method == "POST":
        tipo = (request.POST.get("tipo") or "").strip().lower()
        archivo = request.FILES.get("archivo")

        if not archivo:
            messages.error(request, "Selecciona un archivo CSV.")
            return redirect("carga_masiva")

        try:
            raw = archivo.read()
            text = raw.decode("utf-8-sig")
        except Exception:
            messages.error(request, "No se pudo leer el archivo. Usa CSV en UTF-8.")
            return redirect("carga_masiva")

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            messages.error(request, "CSV inválido (sin encabezados).")
            return redirect("carga_masiva")

        creados = 0
        actualizados = 0
        errores = []

        if tipo == "inventario":
            requeridos = {
                "nombre_insumo",
                "categoria_insumo",
                "unidad_medida",
                "stock_minimo",
                "precio_compra_referencia",
                "iva_porcentaje",
                "estado_insumo",
            }
            faltan = requeridos - set([h.strip() for h in reader.fieldnames if h])
            if faltan:
                messages.error(
                    request,
                    f"Faltan columnas requeridas: {', '.join(sorted(faltan))}",
                )
                return redirect("carga_masiva")

            nombres_vistos = set()
            for idx, row in enumerate(reader, start=2):
                try:
                    nombre = (row.get("nombre_insumo") or "").strip()
                    nombre_norm = _nombre_normalizado(nombre)
                    if not nombre_norm:
                        raise ValueError("nombre_insumo vacío")
                    if nombre_norm in nombres_vistos:
                        raise ValueError("nombre_insumo duplicado dentro del CSV")
                    nombres_vistos.add(nombre_norm)

                    defaults = {
                        "categoria_insumo": (row.get("categoria_insumo") or "").strip(),
                        "unidad_medida": (row.get("unidad_medida") or "").strip(),
                        "stock_actual": _to_decimal(row.get("stock_actual"), default=_to_decimal("0")),
                        "stock_minimo": _to_decimal(row.get("stock_minimo"), default=_to_decimal("0")),
                        "stock_maximo": _to_decimal(row.get("stock_maximo"), default=None),
                        "precio_compra_referencia": _to_decimal(row.get("precio_compra_referencia"), default=_to_decimal("0")),
                        "iva_porcentaje": _to_decimal(row.get("iva_porcentaje"), default=_to_decimal("0")),
                        "estado_insumo": (row.get("estado_insumo") or "disponible").strip(),
                    }

                    with transaction.atomic():
                        candidatos = list(Inventario.objects.select_for_update().filter(nombre_insumo__iexact=nombre))
                        if len(candidatos) > 1:
                            raise ValueError("ya existen múltiples insumos con ese nombre en la base de datos")
                        obj = candidatos[0] if candidatos else None

                        if obj:
                            for k, v in defaults.items():
                                if v is not None and v != "":
                                    setattr(obj, k, v)
                            obj.save()
                            actualizados += 1
                        else:
                            defaults["nombre_insumo"] = nombre
                            Inventario.objects.create(**defaults)
                            creados += 1
                except Exception as e:
                    errores.append(f"L{idx}: {e}")

        elif tipo == "productos":
            requeridos = {
                "nombre_producto",
                "descripcion_producto",
                "precio_venta",
                "es_combo",
                "esta_disponible",
            }
            faltan = requeridos - set([h.strip() for h in reader.fieldnames if h])
            if faltan:
                messages.error(
                    request,
                    f"Faltan columnas requeridas: {', '.join(sorted(faltan))}",
                )
                return redirect("carga_masiva")

            nombres_vistos = set()
            for idx, row in enumerate(reader, start=2):
                try:
                    nombre = (row.get("nombre_producto") or "").strip()
                    nombre_norm = _nombre_normalizado(nombre)
                    if not nombre_norm:
                        raise ValueError("nombre_producto vacío")
                    if nombre_norm in nombres_vistos:
                        raise ValueError("nombre_producto duplicado dentro del CSV")
                    nombres_vistos.add(nombre_norm)

                    def _bool(s):
                        return str(s).strip().lower() in ("1", "true", "si", "sí", "yes")

                    defaults = {
                        "descripcion_producto": (row.get("descripcion_producto") or "").strip() or None,
                        "precio_venta": _to_decimal(row.get("precio_venta"), default=_to_decimal("0")),
                        "es_combo": _bool(row.get("es_combo")),
                        "esta_disponible": _bool(row.get("esta_disponible")),
                        "registro_movimiento_inicial": (row.get("registro_movimiento_inicial") or "").strip() or None,
                        "imagen_catalogo": (row.get("imagen_catalogo") or "").strip(),
                    }

                    with transaction.atomic():
                        candidatos = list(Producto.objects.select_for_update().filter(nombre_producto__iexact=nombre))
                        if len(candidatos) > 1:
                            raise ValueError("ya existen múltiples productos con ese nombre en la base de datos")
                        obj = candidatos[0] if candidatos else None

                        if obj:
                            for k, v in defaults.items():
                                if v is not None:
                                    setattr(obj, k, v)
                            obj.save()
                            actualizados += 1
                        else:
                            defaults["nombre_producto"] = nombre
                            Producto.objects.create(**defaults)
                            creados += 1
                except Exception as e:
                    errores.append(f"L{idx}: {e}")
        else:
            messages.error(request, "Tipo de carga no válido.")
            return redirect("carga_masiva")

        resumen = {
            "tipo": tipo,
            "creados": creados,
            "actualizados": actualizados,
            "errores": errores[:50],
        }
        if errores:
            messages.warning(
                request,
                f"Carga completada con errores. Creados: {creados}, actualizados: {actualizados}.",
            )
        else:
            messages.success(
                request,
                f"Carga completada. Creados: {creados}, actualizados: {actualizados}.",
            )

    return render(request, "dashboard/carga_masiva.html", {"resumen": resumen})


@super_admin_required
@require_http_methods(["GET", "POST"])
def ver_configuracion(request):
    """Listado y edición de configuración del sistema."""
    from dashboard.models import ConfiguracionSistema
    from django.shortcuts import redirect
    from django.contrib import messages

    # Obtener la configuración del sistema, usando el singleton central
    config = ConfiguracionSistema.get_config()

    if request.method == 'POST':
        # Actualizar campos
        config.nombre_sistema = request.POST.get('nombre_sistema', config.nombre_sistema)
        hora_apertura_str = request.POST.get('hora_apertura', config.hora_apertura.strftime('%H:%M'))
        hora_cierre_str = request.POST.get('hora_cierre', config.hora_cierre.strftime('%H:%M'))
        config.porcentaje_iva = request.POST.get('porcentaje_iva', config.porcentaje_iva)
        config.umbral_bonos = request.POST.get('umbral_bonos', config.umbral_bonos)

        try:
            config.hora_apertura = datetime.strptime(hora_apertura_str, '%H:%M').time()
            config.hora_cierre = datetime.strptime(hora_cierre_str, '%H:%M').time()
        except ValueError:
            messages.error(request, 'Formato de hora inválido. Usa HH:MM con horas de 00 a 23.')
            return redirect('ver_configuracion')

        try:
            config.full_clean()  # Validar
            config.save()
            messages.success(request, 'Configuración actualizada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al guardar: {e}')
        
        return redirect('ver_configuracion')

    return render(request, "dashboard/configuracion_sistema.html", {"config": config})


@admin_shori_required
@require_GET
def nuevos_pedidos_api(request):
    ultimo = Pedido.objects.order_by("-id").values(
        "id", "estado_pedido", "fecha_pedido", "usuario__primer_nombre"
    ).first()
    pendientes = Pedido.objects.filter(estado_pedido="pendiente").count()

    if not ultimo:
        return JsonResponse(
            {
                "ultimo_pedido_id": 0,
                "pendientes": pendientes,
                "fecha_ultimo_pedido": "",
                "cliente_ultimo_pedido": "",
                "estado_ultimo_pedido": "",
            }
        )

    return JsonResponse(
        {
            "ultimo_pedido_id": int(ultimo["id"]),
            "pendientes": pendientes,
            "fecha_ultimo_pedido": (
                ultimo["fecha_pedido"].strftime("%Y-%m-%d %H:%M")
                if ultimo.get("fecha_pedido")
                else ""
            ),
            "cliente_ultimo_pedido": ultimo.get("usuario__primer_nombre") or "",
            "estado_ultimo_pedido": ultimo.get("estado_pedido") or "",
        }
    )


def _backup_folder():
    base_dir = Path(__file__).resolve().parents[1]
    backups_dir = base_dir / 'db_backups'
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def _resolve_allowed_path(base_dir: Path, value: str) -> Path:
    """Resuelve una ruta sólo dentro del directorio base permitido."""
    candidate = Path(value).expanduser()
    resolved = candidate.resolve() if candidate.is_absolute() else (base_dir / candidate).resolve()
    base = base_dir.resolve()
    resolved.relative_to(base)
    return resolved


def _try_mysqldump_backup(request, database, backups_dir, backup_nombre):
    """Intenta crear respaldo usando mysqldump"""
    try:
        db_name = database.get('NAME')
        db_user = database.get('USER')
        db_password = database.get('PASSWORD', '')
        db_host = database.get('HOST', 'localhost')
        db_port = database.get('PORT', '3306')

        if not db_name or not db_user:
            return False

        # Intentar encontrar mysqldump en XAMPP primero
        mysqldump_path = shutil.which('mysqldump')
        if not mysqldump_path:
            # Rutas comunes de XAMPP en Windows
            xampp_paths = [
                'C:\\xampp\\mysql\\bin\\mysqldump.exe',
                'C:\\xampp2\\mysql\\bin\\mysqldump.exe',
                'D:\\xampp\\mysql\\bin\\mysqldump.exe',
            ]
            for path in xampp_paths:
                if os.path.exists(path):
                    mysqldump_path = path
                    break
        
        if not mysqldump_path:
            return False

        backup_sql = backup_nombre + '.sql'
        destino = backups_dir / backup_sql

        # Comando mysqldump con opciones para compatibilidad
        cmd = [
            mysqldump_path,
            f'--user={db_user}',
            f'--password={db_password}',
            f'--host={db_host}',
            f'--port={db_port}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--default-character-set=utf8mb4',
            '--skip-lock-tables',
            '--skip-add-locks',
            db_name
        ]

        with open(destino, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return False

        messages.success(request, f'Respaldo MySQL creado: {backup_sql}')
        return True
        
    except Exception:
        return False


def _try_python_mysql_backup(request, database, backups_dir, backup_nombre):
    """Intenta crear respaldo usando Python puro (sin mysqldump)"""
    try:
        import pymysql
        from django.db import connection
        
        db_name = database.get('NAME')
        db_user = database.get('USER')
        db_password = database.get('PASSWORD', '')
        db_host = database.get('HOST', 'localhost')
        db_port = int(database.get('PORT', '3306'))

        if not db_name or not db_user:
            return False

        backup_sql = backup_nombre + '.sql'
        destino = backups_dir / backup_sql

        # Conectar directamente a la base de datos
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            charset='utf8mb4',
            connect_timeout=10
        )

        with open(destino, 'w', encoding='utf-8') as f:
            # Escribir encabezado del respaldo
            f.write(f"-- Resaldo de base de datos: {db_name}\n")
            f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Creado con Python puro (alternativa a mysqldump)\n\n")

            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            for table in tables:
                safe_table = ''.join(ch for ch in table if ch.isalnum() or ch == '_')
                if not safe_table or safe_table != table:
                    continue

                safe_identifier = connection.ops.quote_name(safe_table)

                f.write(f"-- Estructura de tabla: {safe_table}\n")
                f.write("DROP TABLE IF EXISTS {0};\n".format(safe_identifier))

                # Obtener estructura CREATE TABLE
                cursor.execute("SHOW CREATE TABLE {0}".format(safe_identifier))
                create_table = cursor.fetchone()[1]
                f.write(create_table + ";\n\n")

                # Obtener datos
                cursor.execute("SELECT * FROM {0}".format(safe_identifier))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                if rows:
                    f.write(f"-- Datos de tabla: {table}\n")
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            else:
                                # Escapar comillas y caracteres especiales
                                escaped = str(value).replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')
                                values.append(f"'{escaped}'")
                        f.write(f"INSERT INTO `{table}` VALUES ({', '.join(values)});\n")
                    f.write("\n")
                
                f.write("-- Fin de tabla\n\n")

            cursor.close()
            conn.close()

        messages.success(request, f'Respaldo MySQL creado con Python: {backup_sql}')
        return True
        
    except ImportError:
        messages.error(request, 'Instala pymysql: pip install pymysql')
        return False
    except Exception as e:
        messages.error(request, f'Error en respaldo Python: {str(e)}')
        return False


@super_admin_required
@require_GET
def lista_respaldos(request):
    backups_dir = _backup_folder()
    archivos = sorted(
        [f for f in backups_dir.iterdir() if f.is_file() and f.suffix in ['.sqlite3', '.db', '.sqlite', '.sql']],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    backups = []
    for archivo in archivos:
        stat = archivo.stat()
        backups.append({
            'name': archivo.name,
            'size': stat.st_size,
            'mtime': stat.st_mtime,
        })
    return render(request, 'dashboard/respaldo_base_datos.html', {
        'backups': backups,
    })


@super_admin_required
@require_POST
def crear_respaldo(request):
    if request.method != 'POST':
        return redirect('lista_respaldos')

    from django.conf import settings
    database = settings.DATABASES.get('default', {})
    engine = database.get('ENGINE', '')
    if 'sqlite3' not in engine and 'mysql' not in engine:
        messages.error(
            request,
            f'No se pudo crear el respaldo. Database ENGINE no compatible: "{engine}". Solo SQLite y MySQL son soportados.'
        )
        return redirect('lista_respaldos')

    backups_dir = _backup_folder()
    backup_nombre = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if 'sqlite3' in engine:
        nombre_db = database.get('NAME')
        if not nombre_db:
            messages.error(request, 'No se encontró la configuración de la base de datos.')
            return redirect('lista_respaldos')

        try:
            archivo_origen = _resolve_allowed_path(Path(__file__).resolve().parents[1], str(nombre_db))
        except (ValueError, OSError, RuntimeError):
            messages.error(request, 'Ruta de base de datos no válida.')
            return redirect('lista_respaldos')

        if not archivo_origen.exists() or not archivo_origen.is_file():
            messages.error(request, 'Archivo de base de datos no encontrado.')
            return redirect('lista_respaldos')

        backup_nombre += archivo_origen.suffix
        destino = backups_dir / backup_nombre
        try:
            shutil.copy2(str(archivo_origen), str(destino))
            messages.success(request, f'Respaldo creado: {backup_nombre}')
        except Exception as e:
            messages.error(request, f'No se pudo crear el respaldo: {e}')

    elif 'mysql' in engine:
        # Intentar respaldo con mysqldump primero
        mysqldump_success = _try_mysqldump_backup(request, database, backups_dir, backup_nombre)
        
        if not mysqldump_success:
            # Si mysqldump falla, intentar con Python puro
            python_success = _try_python_mysql_backup(request, database, backups_dir, backup_nombre)
            
            if not python_success:
                messages.error(request, 'No se pudo crear el respaldo MySQL con ningún método disponible.')
        
        return redirect('lista_respaldos')

    return redirect('lista_respaldos')


@super_admin_required
@require_GET
def descargar_respaldo(request, filename):
    backups_dir = _backup_folder()
    raw_name = str(filename or '').strip()
    safe_name = os.path.basename(raw_name)

    if not safe_name or safe_name in {'.', '..'} or safe_name != raw_name:
        messages.error(request, 'Nombre de archivo no válido.')
        return redirect('lista_respaldos')

    try:
        ruta = _resolve_allowed_path(backups_dir, safe_name)
        ruta.relative_to(backups_dir.resolve())
    except ValueError:
        messages.error(request, 'Ruta no permitida.')
        return redirect('lista_respaldos')
    if not ruta.exists() or not ruta.is_file():
        messages.error(request, 'Archivo de respaldo no encontrado.')
        return redirect('lista_respaldos')
    return FileResponse(open(ruta, 'rb'), as_attachment=True, filename=safe_name)
