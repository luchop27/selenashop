# apps/resenas/admin.py
from django.contrib import admin
from .models import Resena, RespuestaResena


class RespuestaResenaInline(admin.TabularInline):
    """Inline para respuestas a reseñas"""
    model = RespuestaResena
    extra = 0
    fields = ('usuario', 'comentario', 'creado_en')
    readonly_fields = ('creado_en',)
    autocomplete_fields = ('usuario',)


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """
    Panel de administración para reseñas de productos.
    """
    list_display = (
        'id',
        'producto',
        'usuario',
        'calificacion',
        'titulo',
        'verificado',
        'creado_en',
    )
    list_filter = (
        'calificacion',
        'verificado',
        'creado_en',
        'producto__categoria',
    )
    search_fields = (
        'producto__nombre',
        'usuario__email',
        'usuario__nombre',
        'usuario__apellido',
        'titulo',
        'comentario',
    )
    readonly_fields = ('creado_en',)
    autocomplete_fields = ('producto', 'usuario')
    list_editable = ('verificado',)
    
    ordering = ('-creado_en',)
    date_hierarchy = 'creado_en'
    inlines = [RespuestaResenaInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('producto', 'usuario', 'calificacion', 'verificado')
        }),
        ('Contenido de la Reseña', {
            'fields': ('titulo', 'comentario')
        }),
        ('Metadatos', {
            'fields': ('creado_en',),
            'classes': ('collapse',)
        }),
    )


@admin.register(RespuestaResena)
class RespuestaResenaAdmin(admin.ModelAdmin):
    """Panel de administración para respuestas a reseñas"""
    list_display = ('id', 'resena', 'usuario', 'creado_en')
    list_filter = ('creado_en',)
    search_fields = ('comentario', 'usuario__email', 'resena__usuario__email')
    readonly_fields = ('creado_en', 'actualizado_en')
    autocomplete_fields = ('resena', 'usuario')
    
    fieldsets = (
        ('Información', {
            'fields': ('resena', 'usuario')
        }),
        ('Respuesta', {
            'fields': ('comentario',)
        }),
        ('Metadatos', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    
    def has_add_permission(self, request):
        """
        Permitir agregar reseñas desde el admin
        """
        return True
    
    def has_change_permission(self, request, obj=None):
        """
        Permitir editar reseñas (por si hay contenido inapropiado)
        """
        return True
    
    def has_delete_permission(self, request, obj=None):
        """
        Permitir eliminar reseñas
        """
        return True
