from django.db import models

# Modelo para Categorías
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo para Subcategorías
class Subcategoria(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nombre', 'categoria')

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

# Modelo para Marcas
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

# Modelo para Proveedores
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo para Productos Base
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Código único del producto")
    
    condicion = models.CharField(
        max_length=50, 
        choices=[
            ('Nuevo', 'Nuevo'), 
            ('Usado', 'Usado'), 
            ('Averiado', 'Averiado')
        ], 
        default='Nuevo'
    )
    
    estado = models.CharField(
        max_length=20, 
        default='Disponible', 
        choices=[
            ('Disponible', 'Disponible'), 
            ('Vendido', 'Vendido'), 
            ('Reservado', 'Reservado')
        ]
    )
    
    # Se cambia on_delete a CASCADE para asegurar que un producto siempre tenga categoría y marca.
    # Si eliminas una categoría o marca, sus productos asociados también se eliminarán.
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Modelo para Tipos de Atributos (e.g., Talla, Color)
class Atributo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej. 'Talla', 'Color', 'Material'")
    
    def __str__(self):
        return self.nombre

# Modelo para los Valores de los Atributos (e.g., S, Azul)
class ValorAtributo(models.Model):
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE)
    valor = models.CharField(max_length=100, help_text="Ej. 'M', 'Azul', 'Algodón'")
    
    class Meta:
        unique_together = ('atributo', 'valor')

    def __str__(self):
        return f"{self.atributo.nombre}: {self.valor}"

# Modelo para las Variaciones de Productos (e.g., Camiseta Roja Talla M)
class VariacionProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name='variaciones', on_delete=models.CASCADE)
    atributos = models.ManyToManyField(ValorAtributo)
    
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="SKU de la variación")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        atributos_str = ', '.join([str(val) for val in self.atributos.all()])
        return f"{self.producto.nombre} ({atributos_str})"

# Modelo para Medidas del Producto (relacionado 1 a 1 con la variación)
class MedidasProducto(models.Model):
    variacion = models.OneToOneField(
        'VariacionProducto', 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='medidas'
    )
    peso_gramos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    alto_cm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ancho_cm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profundidad_cm = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Medidas para: {self.variacion.producto.nombre}"

# Modelo para Imágenes del Producto
class ImagenProducto(models.Model):
    variacion = models.ForeignKey(VariacionProducto, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/imagenes/')
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Imagen de {self.variacion}"

# Modelo para el Registro de Ventas
class Venta(models.Model):
    # Se cambia a SET_NULL para mantener un registro histórico de ventas si la variación se elimina
    producto = models.ForeignKey(VariacionProducto, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Venta de {self.producto.nombre if self.producto else 'Producto Eliminado'} - {self.cantidad} unidades"

# Modelo para el Registro de Compras
class Compra(models.Model):
    # Se cambia a SET_NULL para mantener un registro histórico de compras si la variación se elimina
    producto = models.ForeignKey(VariacionProducto, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateField()
    
    def __str__(self):
        return f"Compra de {self.producto.nombre if self.producto else 'Producto Eliminado'} - {self.cantidad} unidades"