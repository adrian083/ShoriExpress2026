from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pedidos, name='lista_pedidos'),
    path('reporte/pdf/', views.descargar_pedidos_pdf, name='descargar_pedidos_pdf'),
    path('checkout/', views.ver_checkout, name='ver_checkout'),
    
    # Vista que procesa la creación del Pedido y DetallePedido
    path('confirmar/', views.finalizar_compra, name='finalizar_compra'),
    
    # Vista para que el cajero cambie el estado (y se active el Signal de stock)
    path('actualizar-estado/<int:pedido_id>/', views.cambiar_estado, name='cambiar_estado'),
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('editar/<int:pk>/', views.editar_pedido, name='editar_pedido'),
    path('eliminar/<int:id>/', views.eliminar_pedido, name='eliminar_pedido'),
]