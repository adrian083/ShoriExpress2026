from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_detalles, name='lista_detalles'),
    path('crear/', views.crear_detalle, name='crear_detalle'),
    path('editar_detalle/<int:id>/', views.editar_detalle, name='editar_detalle'),
    path('eliminar/<int:id>/', views.eliminar_detalle, name='eliminar_detalle'),
]