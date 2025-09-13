from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.forms import inlineformset_factory

from .models import Producto, Atributo, ValorAtributo, VariacionProducto
from .forms import (
    ProductoForm, VariacionProductoFormset,
    AtributoForm, ValorAtributoForm,
    ValorAtributoFormset
)

def lista_productos(request):
    productos = Producto.objects.all()
    contexto = {
        'lista_de_productos': productos,
        'titulo': 'Inventario de Productos'
    }
    return render(request, 'productos/lista.html', contexto)

def detalle_producto(request, id_producto):
    producto = get_object_or_404(Producto.objects.prefetch_related('variaciones'), pk=id_producto)
    variaciones = producto.variaciones.all()
    contexto = {
        'producto': producto,
        'variaciones': variaciones
    }
    return render(request, 'productos/detalle.html', contexto)

def crear_producto_rapido(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        formset = VariacionProductoFormset(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            producto = form.save()
            
            for form_variacion in formset:
                variacion = form_variacion.save(commit=False)
                variacion.producto = producto
                variacion.save()
                
                atributos_seleccionados = form_variacion.cleaned_data['atributos_seleccionados']
                variacion.atributos.set(atributos_seleccionados)
            
            return redirect('lista_productos')
    else:
        form = ProductoForm()
        formset = VariacionProductoFormset()

    contexto = {
        'form': form,
        'formset': formset,
        'titulo': 'Crear Producto Rápido'
    }
    return render(request, 'productos/crear_producto_rapido.html', contexto)

def gestionar_atributos(request):
    if request.method == 'POST':
        if 'crear_atributo' in request.POST:
            form = AtributoForm(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    return redirect('gestionar_atributos')
                except IntegrityError:
                    form.add_error('nombre', 'Este atributo ya existe.')
        
        elif 'agregar_valores' in request.POST:
            atributo_id = request.POST.get('atributo')
            atributo_seleccionado = get_object_or_404(Atributo, pk=atributo_id)
            
            formset_instance = ValorAtributoFormset(request.POST, instance=atributo_seleccionado)
            
            if formset_instance.is_valid():
                formset_instance.save()
                return redirect('gestionar_atributos')

    # Inicializa los formularios para la solicitud GET
    form = AtributoForm()
    
    # Crea un formset vacío para agregar valores
    formset_instance = ValorAtributoFormset(instance=None)
    
    atributos_existentes = Atributo.objects.all().prefetch_related('valoratributo_set')
    
    contexto = {
        'form': form,
        'formset': formset_instance,
        'empty_form': ValorAtributoFormset(instance=None).empty_form,
        'titulo': 'Gestionar Atributos y Valores',
        'atributos_existentes': atributos_existentes,
    }
    return render(request, 'productos/gestionar_atributos.html', contexto)