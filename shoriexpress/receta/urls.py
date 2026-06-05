from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_recetas, name='lista_recetas'),
    path('crear/', views.crear_receta, name='crear_receta'),
    path('editar/<int:id>/', views.editar_receta, name='editar_receta'),
    path('eliminar/<int:id>/', views.eliminar_receta, name='eliminar_receta'),
]