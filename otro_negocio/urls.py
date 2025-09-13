

from django.urls import path
from . import views

urlpatterns = [
    path('', views.resumen_negocio, name='resumen_negocio'),
    path('pagar_deuda/<int:deuda_id>/', views.pagar_deuda, name='pagar_deuda'),
    path('anadir_transaccion/', views.anadir_transaccion, name='anadir_transaccion'), # Correcto
    path('anadir_deuda/', views.anadir_deuda, name='anadir_deuda'), # Correcto
]