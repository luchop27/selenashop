# apps/resenas/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Resena(models.Model):
    """
    Reseñas y calificaciones de las clientas sobre productos.
    Una usuaria puede reseñar un producto solo una vez.
    """
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    titulo = models.CharField(max_length=200, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    verificado = models.BooleanField(
        default=False,
        help_text="Indica si es una compra verificada"
    )

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-creado_en']
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'usuario'],
                name='resenas_uq_producto_usuario'
            )
        ]
        indexes = [
            models.Index(fields=['producto', '-creado_en']),
            models.Index(fields=['calificacion']),
        ]

    def __str__(self):
        return f"Reseña de {self.usuario.email} para {self.producto.nombre} ({self.calificacion}⭐)"
    
    def get_tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido desde la creación"""
        diff = timezone.now() - self.creado_en
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} {'year' if years == 1 else 'years'} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} {'month' if months == 1 else 'months'} ago"
        elif diff.days > 0:
            return f"{diff.days} {'day' if diff.days == 1 else 'days'} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        else:
            return "Just now"


class RespuestaResena(models.Model):
    """
    Respuestas a las reseñas (generalmente del administrador o vendedor)
    """
    resena = models.ForeignKey(
        Resena,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='respuestas_resenas'
    )
    comentario = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Respuesta a Reseña"
        verbose_name_plural = "Respuestas a Reseñas"
        ordering = ['creado_en']

    def __str__(self):
        return f"Respuesta de {self.usuario.email} a reseña de {self.resena.usuario.email}"
    
    def get_tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido desde la creación"""
        diff = timezone.now() - self.creado_en
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} {'year' if years == 1 else 'years'} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} {'month' if months == 1 else 'months'} ago"
        elif diff.days > 0:
            return f"{diff.days} {'day' if diff.days == 1 else 'days'} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        else:
            return "Just now"
