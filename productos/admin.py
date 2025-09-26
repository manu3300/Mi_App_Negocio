from django.contrib import admin
from .models import (
    Categoria, Marca, Proveedor, Producto, VariacionProducto,
    ImagenProducto, Venta, Compra, Atributo, ValorAtributo, Subcategoria,
    MedidasProducto
)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria',)
    list_filter = ('categoria',)
    search_fields = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')
    search_fields = ('nombre', 'contacto')
    
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'subcategoria', 'marca', 'sku', 'estado', 'condicion')
    search_fields = ('nombre', 'sku')
    list_filter = ('categoria', 'subcategoria', 'marca', 'estado', 'condicion')
    
@admin.register(VariacionProducto)
class VariacionProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', '__str__', 'precio_venta', 'stock')
    list_filter = ('producto',)
    search_fields = ('producto__nombre', 'atributos__valor')

@admin.register(MedidasProducto)
class MedidasProductoAdmin(admin.ModelAdmin):
    list_display = ('variacion', 'peso_gramos', 'alto_cm', 'ancho_cm', 'profundidad_cm')
    search_fields = ('variacion__producto__nombre',)

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('variacion',)
    
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'precio_total', 'fecha_venta')
    list_filter = ('fecha_venta',)
    search_fields = ('producto__nombre',)

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'precio_compra', 'proveedor', 'fecha_compra')
    list_filter = ('fecha_compra', 'proveedor')
    search_fields = ('producto__nombre',)

@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(ValorAtributo)
class ValorAtributoAdmin(admin.ModelAdmin):
    list_display = ('atributo', 'valor',)
    search_fields = ('atributo__nombre', 'valor',)
    list_filter = ('atributo',)