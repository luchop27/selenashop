from django.db import models

class PaginaAyuda(models.Model):
    """Modelo para almacenar páginas de ayuda editables desde el admin"""
    
    TIPOS_AYUDA = [
        ('terminos', 'Términos y Condiciones'),
        ('devoluciones', 'Devoluciones y Cambios'),
        ('envios', 'Envíos'),
        ('privacidad', 'Política de Privacidad'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_AYUDA,
        unique=True,
        help_text='Tipo de página de ayuda'
    )
    titulo = models.CharField(
        max_length=200,
        help_text='Título de la página'
    )
    contenido = models.TextField(
        help_text='Contenido HTML o texto de la página'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Activar/Desactivar esta página de ayuda'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Página de Ayuda'
        verbose_name_plural = 'Páginas de Ayuda'
        ordering = ['tipo']
    
    def __str__(self):
        return f"{self.get_tipo_display()}"
    
    def save(self, *args, **kwargs):
        """Asegura que solo haya un registro activo por tipo"""
        if self.activo:
            PaginaAyuda.objects.filter(tipo=self.tipo, activo=True).exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)


class CategoriaFAQ(models.Model):
    """Categorías de preguntas frecuentes"""
    
    nombre = models.CharField(
        max_length=100,
        help_text='Nombre de la categoría (ej: Compras, Pagos, Envíos)'
    )
    descripcion = models.CharField(
        max_length=300,
        blank=True,
        help_text='Descripción breve de la categoría'
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Orden de aparición en el frontend'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Mostrar/Ocultar esta categoría'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría FAQ'
        verbose_name_plural = 'Categorías FAQ'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class PreguntaFrecuente(models.Model):
    """Modelo para preguntas frecuentes"""
    
    categoria = models.ForeignKey(
        CategoriaFAQ,
        on_delete=models.CASCADE,
        related_name='preguntas',
        help_text='Categoría a la que pertenece'
    )
    pregunta = models.CharField(
        max_length=300,
        help_text='Texto de la pregunta'
    )
    respuesta = models.TextField(
        help_text='Respuesta a la pregunta (puede contener HTML básico)'
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Orden dentro de la categoría'
    )
    destacada = models.BooleanField(
        default=False,
        help_text='Mostrar esta pregunta destacada'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Mostrar/Ocultar esta pregunta'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pregunta Frecuente'
        verbose_name_plural = 'Preguntas Frecuentes'
        ordering = ['categoria', 'orden', 'pregunta']
    
    def __str__(self):
        return self.pregunta[:60]


class DatosContacto(models.Model):
    """Modelo para almacenar información de contacto de la tienda"""
    
    direccion = models.CharField(
        max_length=300,
        default='Av. 25 de Junio y Páez, Machala, El Oro',
        help_text='Dirección de la tienda'
    )
    email = models.EmailField(
        default='selenastore.oficial.ec@gmail.com',
        help_text='Email de contacto principal'
    )
    telefono = models.CharField(
        max_length=20,
        default='0979184413',
        help_text='Número de teléfono'
    )
    whatsapp_pedidos = models.CharField(
        max_length=20,
        default='0979184413',
        help_text='Número de WhatsApp donde llegarán los pedidos (sin código de país o con el, ej: 593979184413)'
    )
    facebook = models.URLField(
        blank=True,
        help_text='URL de Facebook (opcional)'
    )
    instagram = models.URLField(
        blank=True,
        help_text='URL de Instagram (opcional)'
    )
    
    # Configuraciones de la tienda (Toggles)
    mostrar_guia_tallas = models.BooleanField(
        default=False,
        help_text='Activar o desactivar el enlace "Encuentra tu talla" en los productos'
    )
    mostrar_envios_devoluciones = models.BooleanField(
        default=True,
        help_text='Activar o desactivar la sección "Envío y Devolución" en los productos'
    )
    
    tiktok = models.URLField(
        blank=True,
        help_text='URL de TikTok (opcional)'
    )
    twitter = models.URLField(
        blank=True,
        help_text='URL de Twitter/X (opcional)'
    )
    google_maps_url = models.URLField(
        blank=True,
        help_text='URL de Google Maps para la ubicación de la tienda (ej: https://maps.app.goo.gl/...)'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Datos de Contacto'
        verbose_name_plural = 'Datos de Contacto'
    
    def __str__(self):
        return 'Información de Contacto de la Tienda'
    
    def save(self, *args, **kwargs):
        """Asegura que solo exista un registro"""
        if not self.pk and DatosContacto.objects.exists():
            self.pk = DatosContacto.objects.first().pk
        super().save(*args, **kwargs)
