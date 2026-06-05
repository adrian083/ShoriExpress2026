from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_inventario, name='lista_inventario'),
    path('reporte/pdf/', views.descargar_inventario_pdf, name='descargar_inventario_pdf'),
    path('crear/', views.crear_insumo, name='crear_insumo'),
    path('editar/<int:id>/', views.editar_insumo, name='editar_insumo'),
    path('eliminar/<int:id>/', views.eliminar_insumo, name='eliminar_insumo'),
]