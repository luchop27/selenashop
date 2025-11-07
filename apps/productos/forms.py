from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Variante, Imagen, Categoria, Coleccion


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'slug', 'categoria', 'coleccion', 'tipo',
            'descripcion_corta', 'descripcion_larga', 'marca',
            'precio_base', 'tiene_tallas', 'activo'
        ]
        widgets = {
            # Ajustes de clases para que coincidan con el CSS del template admin-ecomus
            'nombre': forms.TextInput(attrs={'class': 'mb-10 tf-input', 'placeholder': 'Título del producto'}),
            'slug': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'slug-ejemplo'}),
            'categoria': forms.Select(attrs={'class': 'tf-input', 'placeholder': 'Seleccionar categoría'}),
            'coleccion': forms.Select(attrs={'class': 'tf-input', 'placeholder': 'Seleccionar colección'}),
            'tipo': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Tipo (ej: vestido)'}),
            'descripcion_corta': forms.Textarea(attrs={'rows': 2, 'class': 'tf-input mb-10', 'placeholder': 'Descripción corta del producto'}),
            'descripcion_larga': forms.Textarea(attrs={'rows': 4, 'class': 'tf-input', 'placeholder': 'Descripción larga del producto'}),
            'marca': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Marca'}),
            'precio_base': forms.NumberInput(attrs={'class': 'tf-input', 'placeholder': 'Precio base'}),
            'tiene_tallas': forms.CheckboxInput(attrs={'class': 'tf-checkbox'}),
            'activo': forms.CheckboxInput(attrs={'class': 'tf-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo categorías activas y ordenar por nombre
        self.fields['categoria'].queryset = Categoria.objects.filter(estado=True).order_by('nombre')
        # Filtrar solo colecciones activas y ordenar por nombre
        self.fields['coleccion'].queryset = Coleccion.objects.filter(activo=True).order_by('nombre')
        # Hacer que los campos tengan etiquetas en español
        self.fields['categoria'].label = 'Categoría'
        self.fields['coleccion'].label = 'Colección'
        self.fields['categoria'].empty_label = 'Seleccionar categoría'
        self.fields['coleccion'].empty_label = 'Seleccionar colección (opcional)'


class VarianteForm(forms.ModelForm):
    class Meta:
        model = Variante
        fields = ['talla', 'color', 'sku', 'precio', 'stock']
        widgets = {
            'talla': forms.Select(attrs={'class': 'tf-input'}),
            'color': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Color'}),
            'sku': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Enter SKU'}),
            'precio': forms.NumberInput(attrs={'class': 'tf-input', 'placeholder': 'Sale Price'}),
            'stock': forms.NumberInput(attrs={'class': 'tf-input', 'placeholder': 'Stock'}),
        }


class ImagenForm(forms.ModelForm):
    class Meta:
        model = Imagen
        # The admin selects a file in the file manager and we store the resulting URL only.
        fields = ['url', 'variante']
        widgets = {
            'url': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Seleccionar archivo desde el administrador de archivos'}),
            'variante': forms.HiddenInput(),
        }


VarianteFormSet = inlineformset_factory(
    parent_model=Producto,
    model=Variante,
    form=VarianteForm,
    extra=1,
    can_delete=True,
)

ImagenFormSet = inlineformset_factory(
    parent_model=Producto,
    model=Imagen,
    form=ImagenForm,
    extra=1,
    can_delete=True,
)
