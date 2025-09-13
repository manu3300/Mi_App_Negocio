from django import forms
from .models import Transaccion, Deuda, Persona

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['producto', 'persona', 'tipo', 'cantidad', 'precio_unidad', 'pago_completo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'persona': forms.Select(attrs={'class': 'form-select'}),
            'pago_completo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DeudaForm(forms.ModelForm):
    class Meta:
        model = Deuda
        fields = ['persona', 'tipo', 'monto', 'descripcion']
        widgets = {
            'persona': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }