from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('menu/', views.index, name='index'),
    
    # API endpoints
    path('api/horario/', views.api_configuracion_horario, name='api_horario'),
    
    # Rutas para el carrito (lógica de sesión)
    path('carrito/agregar/<int:producto_id>/', views.agregar_item, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_item, name='eliminar_del_carrito'),
    path('carrito/restar/<int:producto_id>/', views.restar_producto, name='restar_producto'),
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('toggle/<int:producto_id>/', views.toggle_disponible, name='toggle_disponible'),
]