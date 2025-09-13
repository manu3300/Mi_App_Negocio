from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

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
    
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

# --- NUEVOS MODELOS PARA LA GESTIÓN DE ATRIBUTOS ---
class Atributo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej. 'Talla', 'Color', 'Material'")
    
    def __str__(self):
        return self.nombre

class ValorAtributo(models.Model):
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE)
    valor = models.CharField(max_length=100, help_text="Ej. 'M', 'Azul', 'Algodón'")
    
    class Meta:
        unique_together = ('atributo', 'valor')

    def __str__(self):
        return f"{self.atributo.nombre}: {self.valor}"

# --- MODELO VARIACIONPRODUCTO MODIFICADO ---
class VariacionProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name='variaciones', on_delete=models.CASCADE)
    
    # Usamos ManyToManyField para asociar múltiples valores de atributos
    atributos = models.ManyToManyField(ValorAtributo)
    
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="SKU de la variación")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        # Genera una cadena con los atributos, ej: 'Camisa - Talla: M, Color: Azul'
        atributos_str = ', '.join([str(val) for val in self.atributos.all()])
        return f"{self.producto.nombre} ({atributos_str})"

# --- MODELO IMAGENPRODUCTO MODIFICADO ---
class ImagenProducto(models.Model):
    variacion = models.ForeignKey(VariacionProducto, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/imagenes/')
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Imagen de {self.variacion}"

class Venta(models.Model):
    producto = models.ForeignKey(VariacionProducto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Venta de {self.producto.nombre} - {self.cantidad} unidades"

class Compra(models.Model):
    producto = models.ForeignKey(VariacionProducto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateField()
    
    def __str__(self):
        return f"Compra de {self.producto.nombre} - {self.cantidad} unidades"