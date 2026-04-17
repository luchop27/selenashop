from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Variante, Imagen, Categoria, Coleccion


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'slug', 'categoria', 'coleccion', 'tipo',
            'descripcion_corta', 'descripcion_larga', 'marca',
            'precio_base', 'tiene_tallas', 'bajo_pedido'
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
            'tiene_tallas': forms.CheckboxInput(attrs={'class': 'tf-checkbox', 'style': 'width: 21px; height: 21px;'}),
            'bajo_pedido': forms.CheckboxInput(attrs={'class': 'tf-checkbox', 'style': 'width: 21px; height: 21px;'}),
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
    
    def save(self, commit=True):
        """
        Si no se selecciona una colección, asignar automáticamente a la colección 'Básica'.
        Si no existe, la crea automáticamente.
        Los productos siempre se crean activos por defecto.
        """
        instance = super().save(commit=False)
        
        # Siempre establecer productos como activos
        instance.activo = True
        
        # Si no se ha seleccionado ninguna colección
        if not instance.coleccion:
            # Obtener o crear la colección "Básica"
            coleccion_basica, created = Coleccion.objects.get_or_create(
                slug='basica',
                defaults={
                    'nombre': 'Básica',
                    'descripcion': 'Colección por defecto para productos sin colección específica',
                    'activo': True,
                    'destacada': False
                }
            )
            instance.coleccion = coleccion_basica
        
        if commit:
            instance.save()
        return instance


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


# -----------------------------
# FORMULARIOS PARA CATEGORÍA
# -----------------------------
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'slug', 'descripcion', 'imagen', 'coleccion', 'padre', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Nombre de la categoría'}),
            'slug': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'slug-ejemplo'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'tf-input', 'placeholder': 'Descripción de la categoría'}),
            'imagen': forms.FileInput(attrs={'class': 'tf-input'}),
            'coleccion': forms.Select(attrs={'class': 'tf-input'}),
            'padre': forms.Select(attrs={'class': 'tf-input'}),
            'estado': forms.CheckboxInput(attrs={'class': 'tf-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo colecciones activas
        self.fields['coleccion'].queryset = Coleccion.objects.filter(activo=True).order_by('nombre')
        self.fields['coleccion'].empty_label = 'Sin colección'
        # Filtrar solo categorías padre (sin padre)
        self.fields['padre'].queryset = Categoria.objects.filter(padre__isnull=True).order_by('nombre')
        self.fields['padre'].empty_label = 'Ninguna (Categoría principal)'
        # Etiquetas en español
        self.fields['nombre'].label = 'Nombre'
        self.fields['slug'].label = 'Slug'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['imagen'].label = 'Imagen'
        self.fields['coleccion'].label = 'Colección'
        self.fields['padre'].label = 'Categoría padre'
        self.fields['estado'].label = 'Activa'


# -----------------------------
# FORMULARIOS PARA COLECCIÓN
# -----------------------------
class ColeccionForm(forms.ModelForm):
    class Meta:
        model = Coleccion
        fields = ['nombre', 'slug', 'descripcion', 'imagen', 'imagen_mobile', 'activo', 'destacada']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'Nombre de la colección'}),
            'slug': forms.TextInput(attrs={'class': 'tf-input', 'placeholder': 'slug-ejemplo'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'tf-input', 'placeholder': 'Descripción de la colección'}),
            'imagen': forms.FileInput(attrs={'class': 'tf-input'}),
            'imagen_mobile': forms.FileInput(attrs={'class': 'tf-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'tf-checkbox'}),
            'destacada': forms.CheckboxInput(attrs={'class': 'tf-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiquetas en español
        self.fields['nombre'].label = 'Nombre'
        self.fields['slug'].label = 'Slug'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['imagen'].label = 'Imagen Desktop'
        self.fields['imagen_mobile'].label = 'Imagen Mobile'
        self.fields['activo'].label = 'Activa'
        self.fields['destacada'].label = 'Destacada'
