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
    



# ==================== EMAIL VERIFICATION TOKEN ====================
class EmailVerificationToken(models.Model):
    """Token para verificación de email"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='email_tokens')
    token = models.CharField(max_length=100, unique=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Token de verificacion'
        verbose_name_plural = 'Tokens de verificacion'
    
    def __str__(self):
        return f"Token para {self.usuario.email}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            # Generar token único
            import uuid
            self.token = str(uuid.uuid4())
            # Asegurarse de que sea único
            while EmailVerificationToken.objects.filter(token=self.token).exists():
                self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def es_valido(self):
        from datetime import timedelta
        if self.usado:
            return False
        horas = 48
        return timezone.now() <= self.creado + timedelta(hours=horas)
    
    @staticmethod
    def generar_token():
        import uuid
        return str(uuid.uuid4())


# ==================== PASSWORD RESET CODE ====================
class PasswordResetCode(models.Model):
    """Código de 6 caracteres para recuperar contraseña"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reset_codes')
    codigo = models.CharField(max_length=6)
    creado = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Codigo de recuperacion'
        verbose_name_plural = 'Codigos de recuperacion'
    
    def __str__(self):
        return f"Codigo para {self.usuario.email}"
    
    @staticmethod
    def generar_codigo():
        import random
        import string
        caracteres = string.ascii_uppercase + string.digits
        return ''.join(random.choices(caracteres, k=6))
    
    def es_valido(self):
        from datetime import timedelta
        if self.usado:
            return False
        return timezone.now() <= self.creado + timedelta(minutes=15)


# ==================== WISHLIST ====================
class Wishlist(models.Model):
    """Modelo para guardar productos favoritos del usuario"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='wishlist')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='en_wishlist')
    agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'producto')
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        ordering = ['-agregado']
    
    def __str__(self):
        return f"{self.usuario.email} - {self.producto.nombre}"