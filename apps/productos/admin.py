from django.contrib import admin
from .models import Categoria, Marca, Producto, ImagenProducto, VarianteProducto, ResenaProducto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'padre', 'activo', 'orden', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['orden', 'activo']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'texto_alternativo', 'es_principal', 'orden']


class VarianteProductoInline(admin.TabularInline):
    model = VarianteProducto
    extra = 1
    fields = ['sku', 'talla', 'precio', 'stock', 'activo']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sku', 'categoria', 'marca', 'precio', 'stock', 'estado', 'destacado', 'created_at']
    list_filter = ['estado', 'destacado', 'nuevo', 'en_oferta', 'categoria', 'marca', 'created_at']
    search_fields = ['nombre', 'sku', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['destacado', 'precio', 'stock']
    inlines = [ImagenProductoInline, VarianteProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'sku', 'descripcion', 'descripcion_corta')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'marca')
        }),
        ('Precios', {
            'fields': ('precio', 'precio_comparacion', 'precio_costo')
        }),
        ('Inventario', {
            'fields': ('stock', 'stock_minimo')
        }),
        ('SEO', {
            'fields': ('meta_titulo', 'meta_descripcion'),
            'classes': ('collapse',)
        }),
        ('Estados', {
            'fields': ('estado', 'destacado', 'nuevo', 'en_oferta'),
            'description': 'El estado se actualiza automáticamente según el stock'
        }),
    )


@admin.register(ResenaProducto)
class ResenaProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'calificacion', 'compra_verificada', 'aprobado', 'created_at']
    list_filter = ['calificacion', 'compra_verificada', 'aprobado', 'created_at']
    search_fields = ['producto__nombre', 'usuario__username', 'comentario']
    list_editable = ['aprobado']

