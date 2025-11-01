# apps/catalogo/admin.py
from django.contrib import admin
from .models import (
    Categoria,
    Estilo,
    Producto,
    Talla,
    Variante,
    Imagen,
)


# =========================
#  CATEGORÍAS
# =========================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'slug',
        'padre',
        'tipo',
        'estado',
        'posicion',
        'created_at',
    )
    list_filter = ('estado', 'tipo', 'created_at')
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('estado', 'posicion')
    autocomplete_fields = ('padre',)
    ordering = ('posicion', 'nombre')


# =========================
#  ESTILOS
# =========================
@admin.register(Estilo)
class EstiloAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'slug',
        'activo',
        'posicion',
    )
    list_filter = ('activo',)
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activo', 'posicion')
    ordering = ('posicion', 'nombre')


# =========================
#  INLINES (para Producto)
# =========================
class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1
    # As inline of Producto we don't show producto (it's implicit). Alt/posicion were removed.
    fields = ('url', 'variante')
    autocomplete_fields = ('variante',)


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1
    fields = ('talla', 'color', 'sku', 'precio', 'stock')
    autocomplete_fields = ('talla',)


# =========================
#  PRODUCTOS
# =========================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'slug',
        'categoria',
        'estilo',
        'precio_base',
        'tiene_tallas',
        'activo',
        'created_at',
    )
    list_filter = (
        'activo',
        'tiene_tallas',
        'categoria',
        'estilo',
        'created_at',
    )
    search_fields = ('nombre', 'slug', 'descripcion_corta', 'descripcion_larga')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activo', 'precio_base', 'tiene_tallas')
    inlines = [ImagenInline, VarianteInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('Datos básicos', {
            'fields': (
                'nombre',
                'slug',
                'tipo',
                'descripcion_corta',
                'descripcion_larga',
            )
        }),
        ('Clasificación', {
            'fields': (
                'categoria',
                'estilo',
                'marca',
                'material',
            )
        }),
        ('Venta', {
            'fields': (
                'precio_base',
                'tiene_tallas',
                'activo',
            )
        }),
        ('Tiempos', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# =========================
#  TALLAS
# =========================
@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


# =========================
#  VARIANTES
# (por si quieres editarlas fuera del producto)
# =========================
@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = (
        'producto',
        'talla',
        'color',
        'sku',
        'precio',
        'stock',
        'created_at',
    )
    list_filter = ('talla', 'color', 'producto')
    search_fields = ('sku', 'producto__nombre')
    autocomplete_fields = ('producto', 'talla')
    ordering = ('producto', 'talla', 'color')


# =========================
#  IMÁGENES
# (también las registramos por separado)
# =========================
@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = (
        'url',
        'producto',
        'variante',
    )
    list_filter = ('producto',)
    search_fields = ('url', 'producto__nombre')
    autocomplete_fields = ('producto', 'variante')
    ordering = ('producto', 'url')
