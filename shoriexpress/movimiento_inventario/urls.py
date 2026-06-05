from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_movimientos, name='lista_movimientos'),
    path('crear/', views.crear_movimiento, name='crear_movimiento'),
    path('editar/<int:id>/', views.editar_movimiento, name='editar_movimiento'),
    path('eliminar/<int:id>/', views.eliminar_movimiento, name='eliminar_movimiento'),
]