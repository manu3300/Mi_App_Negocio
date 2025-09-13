from django.db import models
from django.db.models import Sum

class Persona(models.Model):
    """
    Representa a un cliente o proveedor en el sistema.
    """
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('Cliente', 'Cliente'), ('Proveedor', 'Proveedor')])
    contacto = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class Producto(models.Model):
    """
    Representa un producto o artículo que se vende o se compra.
    """
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Cuenta(models.Model):
    """
    Representa una cuenta financiera, como 'Efectivo' o 'Banco'.
    """
    nombre = models.CharField(max_length=100, unique=True) # Ej. 'Efectivo', 'Banco'
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

class Deuda(models.Model):
    """
    Registra una deuda por cobrar o por pagar.
    """
    TIPO_DEUDA_CHOICES = [
        ('Por Cobrar', 'Deuda por Cobrar'),
        ('Por Pagar', 'Deuda por Pagar'),
    ]
    
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_DEUDA_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    esta_pagada = models.BooleanField(default=False)

    def __str__(self):
        # Esta es la parte corregida para evitar el error 'NoneType'
        if self.persona:
            return f"{self.tipo} de ${self.monto} ({self.persona.nombre})"
        else:
            return f"{self.tipo} de ${self.monto} (Persona no especificada)"

class Transaccion(models.Model):
    """
    Registra una venta o compra que afecta el inventario y el dinero.
    """
    TIPO_CHOICES = [
        ('Venta', 'Venta'),
        ('Compra', 'Compra'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    precio_unidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    
    pago_completo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Sobreescribe el método save para gestionar el saldo y las deudas
        automáticamente.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            monto_total = self.cantidad * self.precio_unidad
            
            if self.tipo == 'Venta':
                if self.pago_completo:
                    try:
                        efectivo = Cuenta.objects.get(nombre='Efectivo')
                        efectivo.saldo += monto_total
                        efectivo.save()
                    except Cuenta.DoesNotExist:
                        print("La cuenta 'Efectivo' no existe.")
                else:
                    Deuda.objects.create(
                        persona=self.persona,
                        tipo='Por Cobrar',
                        monto=monto_total,
                        descripcion=f"Venta a crédito a {self.persona.nombre} de {self.cantidad} {self.producto.nombre}"
                    )
            
            elif self.tipo == 'Compra':
                try:
                    efectivo = Cuenta.objects.get(nombre='Efectivo')
                    efectivo.saldo -= monto_total
                    efectivo.save()
                except Cuenta.DoesNotExist:
                    print("La cuenta 'Efectivo' no existe.")

    def __str__(self):
        return f"{self.tipo} de {self.cantidad} {self.producto.nombre}"