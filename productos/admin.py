from django.contrib import admin
from .models import (
    Categoria, Marca, Proveedor, Producto, VariacionProducto,
    ImagenProducto, Venta, Compra, Atributo, ValorAtributo
)

# Admin para el modelo Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# Admin para el modelo Marca
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# Admin para el modelo Proveedor
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')
    search_fields = ('nombre', 'contacto')

# Admin para el modelo Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'marca', 'sku', 'estado', 'condicion')
    search_fields = ('nombre', 'sku')
    list_filter = ('categoria', 'marca', 'estado', 'condicion')
    
# Admin para el modelo VariacionProducto (CORREGIDO)
@admin.register(VariacionProducto)
class VariacionProductoAdmin(admin.ModelAdmin):
    # Ya no usamos 'nombre'. Usamos '__str__' para mostrar la representación de la variación.
    list_display = ('producto', '__str__', 'precio_venta', 'stock')
    list_filter = ('producto',)
    # Ahora la búsqueda se hace a través de los valores de los atributos.
    search_fields = ('producto__nombre', 'atributos__valor')

# Admin para el modelo ImagenProducto
@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('variacion',)
    
# Admin para el modelo Venta
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'precio_total', 'fecha_venta')
    list_filter = ('fecha_venta',)
    search_fields = ('producto__nombre',)

# Admin para el modelo Compra
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'precio_compra', 'proveedor', 'fecha_compra')
    list_filter = ('fecha_compra', 'proveedor')
    search_fields = ('producto__nombre',)

# Admin para los nuevos modelos de Atributos
@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(ValorAtributo)
class ValorAtributoAdmin(admin.ModelAdmin):
    list_display = ('atributo', 'valor',)
    search_fields = ('atributo__nombre', 'valor',)
    list_filter = ('atributo',)