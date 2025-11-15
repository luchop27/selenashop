from django.db import models

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
