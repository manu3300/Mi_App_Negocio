from django.contrib import admin
from .models import Producto, Transaccion, Deuda, Cuenta, Persona

admin.site.register(Producto)
admin.site.register(Transaccion)
admin.site.register(Deuda)
admin.site.register(Cuenta)
admin.site.register(Persona) # ¡Añade esto!