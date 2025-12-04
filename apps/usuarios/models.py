from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


# ==================== PROVINCIA ====================
class Provincia(models.Model):
    """Modelo para almacenar las provincias del Ecuador"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
    
    def __str__(self):
        return self.nombre


# ==================== CIUDAD ====================
class Ciudad(models.Model):
    """Modelo para almacenar las ciudades del Ecuador"""
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        related_name='ciudades'
    )
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        unique_together = ('nombre', 'provincia')
    
    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'admin_tienda')
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('cliente', 'Cliente'),
        ('admin_tienda', 'Administrador de Tienda'),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')

    fecha_registro = models.DateTimeField(default=timezone.now)
    fecha_edicion = models.DateTimeField(auto_now=True)

    # Campos de control de Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.nombre:
            return self.nombre
        return self.email

    def get_short_name(self):
        """Retorna el nombre corto del usuario"""
        return self.nombre if self.nombre else self.email

    def __str__(self):
        return f"{self.email} ({self.rol})"
