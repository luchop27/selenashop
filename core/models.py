from django.db import models
from django.conf import settings

class DeliveryReturnInfo(models.Model):
    """Modelo para gestionar la información de Delivery & Return editable desde el admin"""
    
    # Título del modal
    titulo = models.CharField(
        max_length=100, 
        default='Shipping & Delivery',
        help_text='Título que aparece en el modal'
    )
    
    # Sección Delivery
    delivery_titulo = models.CharField(
        max_length=50, 
        default='Delivery',
        help_text='Título de la sección de envíos'
    )
    delivery_texto_1 = models.TextField(
        default='All orders shipped with UPS Express.',
        help_text='Primera línea de información de envío'
    )
    delivery_texto_2 = models.TextField(
        default='Always free shipping for orders over US $250.',
        help_text='Segunda línea de información de envío'
    )
    delivery_texto_3 = models.TextField(
        default='All orders are shipped with a UPS tracking number.',
        help_text='Tercera línea de información de envío'
    )
    
    # Sección Returns
    returns_titulo = models.CharField(
        max_length=50, 
        default='Returns',
        help_text='Título de la sección de devoluciones'
    )
    returns_texto_1 = models.TextField(
        default='Items returned within 14 days of their original shipment date in same as new condition will be eligible for a full refund or store credit.',
        help_text='Primera línea de información de devoluciones'
    )
    returns_texto_2 = models.TextField(
        default='Refunds will be charged back to the original form of payment used for purchase.',
        help_text='Segunda línea de información de devoluciones'
    )
    returns_texto_3 = models.TextField(
        default='Customer is responsible for shipping charges when making returns and shipping/handling fees of original purchase is non-refundable.',
        help_text='Tercera línea de información de devoluciones'
    )
    returns_texto_4 = models.TextField(
        default='All sale items are final purchases.',
        help_text='Cuarta línea de información de devoluciones'
    )
    
    # Sección Help
    help_titulo = models.CharField(
        max_length=50, 
        default='Help',
        help_text='Título de la sección de ayuda'
    )
    help_texto = models.TextField(
        default='Give us a shout if you have any other questions and/or concerns.',
        help_text='Texto de introducción de ayuda'
    )
    help_email = models.EmailField(
        default='contact@domain.com',
        help_text='Email de contacto'
    )
    help_telefono = models.CharField(
        max_length=50,
        default='+1 (23) 456 789',
        help_text='Teléfono de contacto'
    )
    
    # Control
    activo = models.BooleanField(
        default=True,
        help_text='Solo puede haber un registro activo'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Información de Envío y Devoluciones'
        verbose_name_plural = 'Información de Envío y Devoluciones'
    
    def __str__(self):
        return f"{self.titulo} - {'Activo' if self.activo else 'Inactivo'}"
    
    def save(self, *args, **kwargs):
        """Asegura que solo haya un registro activo"""
        if self.activo:
            # Desactivar todos los demás registros
            DeliveryReturnInfo.objects.filter(activo=True).exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)


# ==================== MODELOS DE PEDIDOS ====================

class Pedido(models.Model):
    """Modelo para almacenar los pedidos realizados por los clientes"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('bank_transfer', 'Transferencia Bancaria'),
        ('cash_on_delivery', 'Pago Contra Entrega'),
    ]
    
    # Información del cliente
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        help_text='Usuario que realizó el pedido (opcional para invitados)'
    )
    email = models.EmailField()
    first_name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellido')
    phone = models.CharField(max_length=20, verbose_name='Teléfono')
    
    # Información de envío
    country = models.CharField(max_length=100, verbose_name='País')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    address = models.TextField(verbose_name='Dirección')
    
    # Información del pedido
    order_note = models.TextField(blank=True, null=True, verbose_name='Notas del pedido')
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='bank_transfer',
        verbose_name='Método de pago'
    )
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gift_wrap = models.BooleanField(default=False, verbose_name='Envoltura de regalo')
    gift_wrap_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Código de descuento')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Monto de descuento')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Estado y fechas
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    # Número de pedido
    numero_pedido = models.CharField(max_length=50, unique=True, editable=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        """Generar número de pedido automáticamente"""
        if not self.numero_pedido:
            import random
            import string
            from django.utils import timezone
            
            # Formato: ORD-YYYYMMDD-XXXX (donde XXXX es aleatorio)
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.numero_pedido = f"ORD-{date_str}-{random_str}"
        
        super().save(*args, **kwargs)


class DetallePedido(models.Model):
    """Detalle de productos incluidos en cada pedido"""
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    variante = models.ForeignKey(
        'productos.Variante',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Información guardada del producto (por si se elimina o modifica)
    nombre_producto = models.CharField(max_length=200)
    talla = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Imagen del producto (guardada por si se elimina)
    imagen_url = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"{self.nombre_producto} x{self.cantidad} - Pedido #{self.pedido.numero_pedido}"
    
    def save(self, *args, **kwargs):
        """Calcular subtotal automáticamente"""
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


# ==================== CÓDIGOS DE DESCUENTO ====================

class CodigoDescuento(models.Model):
    """Modelo para gestionar códigos de descuento"""
    
    TIPO_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='percentage', verbose_name='Tipo de descuento')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    
    # Límites
    monto_minimo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Monto mínimo de compra',
        help_text='Monto mínimo del carrito para aplicar el descuento'
    )
    usos_maximos = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name='Usos máximos',
        help_text='Número máximo de veces que puede usarse (dejar vacío para ilimitado)'
    )
    usos_actuales = models.PositiveIntegerField(default=0, verbose_name='Usos actuales')
    
    # Fechas de validez
    fecha_inicio = models.DateTimeField(verbose_name='Fecha de inicio')
    fecha_expiracion = models.DateTimeField(verbose_name='Fecha de expiración')
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Código de Descuento'
        verbose_name_plural = 'Códigos de Descuento'
    
    def __str__(self):
        tipo_str = f"{self.valor}%" if self.tipo == 'percentage' else f"${self.valor}"
        return f"{self.codigo} - {tipo_str}"
    
    def es_valido(self, monto_carrito=0):
        """Verificar si el código es válido"""
        from django.utils import timezone
        now = timezone.now()
        
        # Verificar si está activo
        if not self.activo:
            return False, "El código de descuento no está activo"
        
        # Verificar fechas
        if now < self.fecha_inicio:
            return False, "El código de descuento aún no está disponible"
        
        if now > self.fecha_expiracion:
            return False, "El código de descuento ha expirado"
        
        # Verificar usos máximos
        if self.usos_maximos and self.usos_actuales >= self.usos_maximos:
            return False, "El código de descuento ha alcanzado su límite de usos"
        
        # Verificar monto mínimo
        if monto_carrito < self.monto_minimo:
            return False, f"El monto mínimo para usar este código es ${self.monto_minimo}"
        
        return True, "Código válido"
    
    def calcular_descuento(self, monto_carrito):
        """Calcular el monto de descuento"""
        if self.tipo == 'percentage':
            descuento = monto_carrito * (self.valor / 100)
        else:
            descuento = self.valor
        
        # No permitir descuentos mayores al monto del carrito
        return min(descuento, monto_carrito)
