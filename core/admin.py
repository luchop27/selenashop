from django.contrib import admin
from .models import DeliveryReturnInfo

@admin.register(DeliveryReturnInfo)
class DeliveryReturnInfoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'activo', 'fecha_modificacion']
    list_filter = ['activo', 'fecha_modificacion']
    search_fields = ['titulo', 'delivery_texto_1', 'returns_texto_1']
    
    fieldsets = (
        ('General', {
            'fields': ('titulo', 'activo')
        }),
        ('Sección: Delivery', {
            'fields': (
                'delivery_titulo',
                'delivery_texto_1',
                'delivery_texto_2',
                'delivery_texto_3',
            )
        }),
        ('Sección: Returns', {
            'fields': (
                'returns_titulo',
                'returns_texto_1',
                'returns_texto_2',
                'returns_texto_3',
                'returns_texto_4',
            )
        }),
        ('Sección: Help', {
            'fields': (
                'help_titulo',
                'help_texto',
                'help_email',
                'help_telefono',
            )
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar solo si hay más de un registro"""
        if DeliveryReturnInfo.objects.count() <= 1:
            return False
        return super().has_delete_permission(request, obj)
