from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_recibos, name='lista_recibos'),
    path('crear/', views.crear_recibo, name='crear_recibo'),
    path('detalle/<int:id>/', views.detalle_recibo, name='detalle_recibo'),
    path('editar/<int:id>/', views.editar_recibo, name='editar_recibo'),
    path('eliminar/<int:id>/', views.eliminar_recibo, name='eliminar_recibo'),
    path('factura/<int:id>/pdf/', views.descargar_factura_pdf, name='descargar_factura_pdf'),
    path('reporte/pdf/', views.descargar_reporte_recibos_pdf, name='descargar_reporte_recibos_pdf'),
]