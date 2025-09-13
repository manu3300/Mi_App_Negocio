from django.db import models

class Herramienta(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.IntegerField(default=1)
    fecha_adquisicion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=[('Nueva', 'Nueva'), ('Usada', 'Usada'), ('Averiada', 'Averiada')], default='Nueva')

    def __str__(self):
        return self.nombre