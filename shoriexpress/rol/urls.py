from django.urls import path
from . import views

urlpatterns = [
    # El nombre (name) es lo que usa el redirect y los enlaces {% url %}
    path('', views.lista_roles, name='lista_roles'),
    path('crear/', views.crear_rol, name='crear_rol'),
    path('editar/<int:id>/', views.editar_rol, name='editar_rol'),
    path('eliminar/<int:id>/', views.eliminar_rol, name='eliminar_rol'),
]