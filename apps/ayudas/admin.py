from django.contrib import admin
from .models import PaginaAyuda, CategoriaFAQ, PreguntaFrecuente, DatosContacto, SliderItem


@admin.register(SliderItem)
class SliderItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'orden', 'activo', 'created_at')
    list_editable = ('orden', 'activo')
    list_filter = ('activo',)
    ordering = ('orden', '-created_at')


@admin.register(PaginaAyuda)
class PaginaAyudaAdmin(admin.ModelAdmin):
    list_display = ('get_tipo_display', 'titulo', 'activo', 'fecha_modificacion')
    list_filter = ('tipo', 'activo', 'fecha_modificacion')
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('tipo', 'titulo', 'activo')
        }),
        ('Contenido', {
            'fields': ('contenido',),
            'classes': ('wide',),
            'description': 'Ingresa el contenido de la página. Puedes usar HTML básico.'
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_tipo_display(self, obj):
        return obj.get_tipo_display()
    get_tipo_display.short_description = 'Tipo de Página'


@admin.register(CategoriaFAQ)
class CategoriaFAQAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'activo', 'get_total_preguntas')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
    
    fieldsets = (
        ('Información', {
            'fields': ('nombre', 'descripcion', 'orden', 'activo')
        }),
    )
    
    def get_total_preguntas(self, obj):
        return obj.preguntas.filter(activo=True).count()
    get_total_preguntas.short_description = 'Preguntas'


@admin.register(PreguntaFrecuente)
class PreguntaFrecuenteAdmin(admin.ModelAdmin):
    list_display = ('pregunta', 'categoria', 'orden', 'destacada', 'activo')
    list_filter = ('categoria', 'destacada', 'activo', 'fecha_creacion')
    search_fields = ('pregunta', 'respuesta')
    ordering = ('categoria', 'orden')
    
    fieldsets = (
        ('Información', {
            'fields': ('categoria', 'pregunta', 'orden', 'destacada', 'activo')
        }),
        ('Respuesta', {
            'fields': ('respuesta',),
            'classes': ('wide',),
            'description': 'Puedes usar HTML básico para formatear (h4, p, ul, li, strong, em, a, etc.)'
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')


@admin.register(DatosContacto)
class DatosContactoAdmin(admin.ModelAdmin):
    list_display = ('email', 'telefono')
    
    fieldsets = (
        ('Información de Contacto', {
            'fields': ('direccion', 'google_maps_url', 'email', 'telefono')
        }),
        ('Redes Sociales', {
            'fields': ('facebook', 'instagram', 'tiktok', 'twitter'),
            'classes': ('collapse',),
            'description': 'URLs completas de tus redes sociales (ej: https://www.facebook.com/...)'
        }),
    )
    
    def has_add_permission(self, request):
        """Evita crear múltiples registros"""
        return not DatosContacto.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Evita eliminar el registro único"""
        return False
