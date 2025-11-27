from django.contrib import admin
from .models import AboutUs, AboutUsImage, DeliveryReturnInfo, Pedido, DetallePedido, CodigoDescuento


# ==================== ABOUT US ADMIN ====================

class AboutUsImageInline(admin.TabularInline):
    """Inline para gestionar imágenes del slider de About Us"""
    model = AboutUs.imagenes_slider.through
    extra = 1
    verbose_name = 'Imagen'
    verbose_name_plural = 'Imágenes del Slider'


@admin.register(AboutUsImage)
class AboutUsImageAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'posicion', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'posicion', 'fecha_creacion']
    search_fields = ['titulo']
    ordering = ['posicion']
    
    fieldsets = (
        ('Información', {
            'fields': ('titulo', 'imagen')
        }),
        ('Configuración', {
            'fields': ('posicion', 'activo')
        }),
    )


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['get_titulo', 'activo', 'fecha_modificacion']
    list_filter = ['activo', 'fecha_modificacion']
    search_fields = ['mision_titulo', 'mision_texto']
    readonly_fields = ['fecha_modificacion']
    
    fieldsets = (
        ('Sección: Misión', {
            'fields': ('mision_titulo', 'mision_texto')
        }),
        ('Slider de Imágenes', {
            'fields': ('imagenes_slider',),
            'description': 'Selecciona las imágenes que deseas mostrar en el slider. Puedes crear nuevas imágenes desde la sección "Imágenes About Us".'
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_titulo(self, obj):
        return f"Página {obj.mision_titulo}"
    get_titulo.short_description = 'Página'
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar solo si hay más de un registro"""
        if AboutUs.objects.count() <= 1:
            return False
        return super().has_delete_permission(request, obj)


# ==================== CÓDIGOS DE DESCUENTO ADMIN ====================

@admin.register(CodigoDescuento)
class CodigoDescuentoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo', 'valor', 'usos_actuales', 'usos_maximos', 'fecha_expiracion', 'activo']
    list_filter = ['activo', 'tipo', 'fecha_inicio', 'fecha_expiracion']
    search_fields = ['codigo', 'descripcion']
    readonly_fields = ['usos_actuales', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'activo')
        }),
        ('Descuento', {
            'fields': ('tipo', 'valor', 'monto_minimo')
        }),
        ('Límites y Usos', {
            'fields': ('usos_maximos', 'usos_actuales')
        }),
        ('Fechas de Validez', {
            'fields': ('fecha_inicio', 'fecha_expiracion')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Convertir código a mayúsculas
        obj.codigo = obj.codigo.upper()
        super().save_model(request, obj, form, change)


# ==================== PEDIDOS ADMIN ====================

class DetallePedidoInline(admin.TabularInline):
    """Inline para mostrar items del pedido"""
    model = DetallePedido
    extra = 0
    readonly_fields = ['producto', 'variante', 'nombre_producto', 'talla', 'color', 
                       'precio_unitario', 'cantidad', 'subtotal', 'imagen_url']
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'first_name', 'last_name', 'email', 'total', 'discount_code', 'estado', 'created_at']
    list_filter = ['estado', 'metodo_pago', 'created_at', 'gift_wrap']
    search_fields = ['numero_pedido', 'email', 'first_name', 'last_name', 'phone', 'discount_code']
    readonly_fields = ['numero_pedido', 'created_at', 'updated_at', 'usuario']
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'estado', 'created_at', 'updated_at')
        }),
        ('Información del Cliente', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Dirección de Envío', {
            'fields': ('country', 'city', 'address')
        }),
        ('Detalles del Pedido', {
            'fields': ('order_note', 'metodo_pago')
        }),
        ('Totales', {
            'fields': ('subtotal', 'gift_wrap', 'gift_wrap_cost', 'discount_code', 'discount_amount', 'total')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Solo permitir eliminar pedidos cancelados"""
        if obj and obj.estado != 'cancelado':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'nombre_producto', 'talla', 'color', 'precio_unitario', 'cantidad', 'subtotal']
    list_filter = ['pedido__estado', 'pedido__created_at']
    search_fields = ['nombre_producto', 'pedido__numero_pedido']
    readonly_fields = ['pedido', 'producto', 'variante', 'nombre_producto', 'talla', 'color', 
                       'precio_unitario', 'cantidad', 'subtotal', 'imagen_url']


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
