import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # or whatever settings is
django.setup()

from apps.usuarios.models import Usuario

email = 'admin@admin.com'
password = 'admin123'

try:
    u = Usuario.objects.get(email=email)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.rol = 'admin_tienda'
    u.save()
    print("User updated")
except Usuario.DoesNotExist:
    u = Usuario.objects.create_user(email=email, password=password)
    u.is_superuser = True
    u.is_staff = True
    u.rol = 'admin_tienda'
    u.save()
    print("User created")
