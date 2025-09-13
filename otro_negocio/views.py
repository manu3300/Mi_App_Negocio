from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

# Importa los modelos y los formularios
from .models import Cuenta, Transaccion, Deuda, Producto, Persona
from .forms import TransaccionForm, DeudaForm

def resumen_negocio(request):
    # Obtener listas de transacciones y deudas
    transacciones_efectivo = Transaccion.objects.all().order_by('-fecha')[:10]
    stock_actual_productos = Producto.objects.all().order_by('nombre')
    deudas_por_cobrar_lista = Deuda.objects.filter(tipo='Por Cobrar', esta_pagada=False).order_by('fecha_creacion')
    deudas_por_pagar_lista = Deuda.objects.filter(tipo='Por Pagar', esta_pagada=False).order_by('fecha_creacion')

    # Calcular los valores totales
    compras = Transaccion.objects.filter(tipo='Compra').aggregate(total=Sum('cantidad'))['total'] or 0
    ventas = Transaccion.objects.filter(tipo='Venta').aggregate(total=Sum('cantidad'))['total'] or 0
    stock_actual = compras - ventas

    deudas_por_cobrar = deudas_por_cobrar_lista.aggregate(total=Sum('monto'))['total'] or 0
    deudas_por_pagar = deudas_por_pagar_lista.aggregate(total=Sum('monto'))['total'] or 0
    
    try:
        efectivo = Cuenta.objects.get(nombre='Efectivo')
        saldo_efectivo = efectivo.saldo
    except Cuenta.DoesNotExist:
        saldo_efectivo = 0

    valor_total = saldo_efectivo + deudas_por_cobrar - deudas_por_pagar

    contexto = {
        'saldo_efectivo': saldo_efectivo,
        'stock_actual': stock_actual,
        'deudas_por_cobrar': deudas_por_cobrar,
        'deudas_por_pagar': deudas_por_pagar,
        'valor_total': valor_total,
        
        'transacciones_efectivo': transacciones_efectivo,
        'stock_actual_productos': stock_actual_productos,
        'deudas_por_cobrar_lista': deudas_por_cobrar_lista,
        'deudas_por_pagar_lista': deudas_por_pagar_lista,
    }

    return render(request, 'otro_negocio/resumen.html', contexto)


@require_http_methods(["POST"])
def pagar_deuda(request, deuda_id):
    deuda = get_object_or_404(Deuda, id=deuda_id)
    deuda.esta_pagada = True
    deuda.save()

    try:
        efectivo = Cuenta.objects.get(nombre='Efectivo')
        efectivo.saldo += deuda.monto
        efectivo.save()
    except Cuenta.DoesNotExist:
        pass
    
    return redirect('resumen_negocio')


def anadir_transaccion(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('resumen_negocio')
    else:
        form = TransaccionForm()
    
    contexto = {'form': form, 'titulo': 'Añadir Nueva Transacción'}
    return render(request, 'otro_negocio/formulario.html', contexto)


def anadir_deuda(request):
    if request.method == 'POST':
        form = DeudaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('resumen_negocio')
    else:
        form = DeudaForm()
    
    contexto = {'form': form, 'titulo': 'Añadir Nueva Deuda'}
    return render(request, 'otro_negocio/formulario.html', contexto)