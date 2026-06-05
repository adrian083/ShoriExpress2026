from django.urls import path
from . import views

urlpatterns = [
    path('configuracion/', views.ver_configuracion, name='ver_configuracion'),
    path('api/dashboard-data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('api/nuevos-pedidos/', views.nuevos_pedidos_api, name='nuevos_pedidos_api'),
    path('backup/', views.lista_respaldos, name='lista_respaldos'),
    path('backup/crear/', views.crear_respaldo, name='crear_respaldo'),
    path('backup/descargar/<str:filename>/', views.descargar_respaldo, name='descargar_respaldo'),
    path('carga-masiva/', views.carga_masiva, name='carga_masiva'),
]