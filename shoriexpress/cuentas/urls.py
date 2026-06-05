from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('logout/', views.logout_view, name='logout'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('menu-completo/', views.ver_menu_publico, name='menu_publico'),
    path('api/hora-bogota/', views.api_hora_bogota, name='api_hora_bogota'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'), 
    path('pedido/detalle/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
]