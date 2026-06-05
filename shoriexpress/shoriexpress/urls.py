"""
URL configuration for shoriexpress project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Página comercial (landing) como página principal ──
    path('', include('cuentas.urls')),

    # ── Dashboard interno (requiere sesión) ──
    path('panel/', home, name='home'),

    # ── Rutas de aplicaciones ──
    path('roles/', include('rol.urls')),
    path('usuarios/', include('usuario.urls')),
    path('inventario/', include('inventario.urls')),
    path('productos/', include('producto.urls')),
    path('recetas/', include('receta.urls')),
    path('movimientos/', include('movimiento_inventario.urls')),
    path('pedidos/', include('pedido.urls')),
    path('detalles/', include('detalle_pedido.urls')),
    path('metodos_pago/', include('metodo_pago.urls')),
    path('recibos/', include('recibo.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Servir archivos multimedia y estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)