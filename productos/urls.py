# En productos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('crear/', views.crear_producto_rapido, name='crear_producto_rapido'),
    # Nueva URL para la gestión de atributos
    path('gestionar_atributos/', views.gestionar_atributos, name='gestionar_atributos'),
    path('<int:id_producto>/', views.detalle_producto, name='detalle_producto'),
]