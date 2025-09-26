from django import forms
from .models import Producto, VariacionProducto, Atributo, ValorAtributo, Subcategoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'subcategoria', 'marca', 'condicion', 'estado', 'sku']

class VariacionProductoForm(forms.ModelForm):
    atributos_seleccionados = forms.ModelMultipleChoiceField(
        queryset=ValorAtributo.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Atributos de la variación"
    )

    class Meta:
        model = VariacionProducto
        fields = ['precio_venta', 'stock']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['atributos_seleccionados'].queryset = ValorAtributo.objects.all()

from django.forms import inlineformset_factory

VariacionProductoFormset = inlineformset_factory(
    Producto, 
    VariacionProducto, 
    form=VariacionProductoForm,
    extra=1,
    can_delete=False
)

class AtributoForm(forms.ModelForm):
    class Meta:
        model = Atributo
        fields = ['nombre']

class ValorAtributoForm(forms.ModelForm):
    class Meta:
        model = ValorAtributo
        fields = ['atributo', 'valor']

ValorAtributoFormset = inlineformset_factory(
    Atributo,
    ValorAtributo,
    form=ValorAtributoForm,
    extra=1,
    can_delete=True
)