# apps/resenas/admin.py
from django.contrib import admin
from .models import Resena


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
        'creado_en',
    )
    list_filter = (
        'calificacion',
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
    
    ordering = ('-creado_en',)
    date_hierarchy = 'creado_en'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('producto', 'usuario', 'calificacion')
        }),
        ('Contenido de la Reseña', {
            'fields': ('titulo', 'comentario')
        }),
        ('Metadatos', {
            'fields': ('creado_en',),
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
