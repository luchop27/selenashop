"""
Script para crear superusuario
"""
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.usuarios.models import Usuario

# Crear superusuario
email = 'admin@selenashop.com'
password = 'admin123'

if Usuario.objects.filter(email=email).exists():
    user = Usuario.objects.get(email=email)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.rol = 'admin_tienda'
    user.save()
    print(f'✅ Superusuario actualizado!')
else:
    user = Usuario.objects.create_superuser(
        email=email,
        password=password,
        nombre='Admin',
        apellido='Selena Shop'
    )
    print(f'✅ Superusuario creado!')

print(f'   Email: {email}')
print(f'   Contraseña: {password}')
print(f'   Accede al admin en: http://127.0.0.1:8000/admin')
