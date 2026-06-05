from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_metodos, name='lista_metodos'),
    path('crear/', views.crear_metodo, name='crear_metodo'),
    path('editar/<int:id>/', views.editar_metodo, name='editar_metodo'),
    path('eliminar/<int:id>/', views.eliminar_metodo, name='eliminar_metodo'),
]