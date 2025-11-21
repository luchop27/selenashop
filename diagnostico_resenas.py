import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.resenas.models import Resena
from apps.usuarios.models import Usuario
from apps.productos.models import Producto

print("=" * 80)
print("DIAGNÓSTICO DE RESEÑAS")
print("=" * 80)

# 1. Verificar usuarios
print("\n1️⃣ USUARIOS EN LA BASE DE DATOS:")
usuarios = Usuario.objects.all()
print(f"   Total usuarios: {usuarios.count()}")
for u in usuarios:
    print(f"   - ID {u.id}: {u.email}")

# 2. Verificar productos
print("\n2️⃣ PRODUCTOS EN LA BASE DE DATOS:")
productos = Producto.objects.all()[:5]
print(f"   Total productos: {Producto.objects.count()}")
for p in productos:
    print(f"   - ID {p.id}: {p.nombre}")

# 3. Verificar reseñas
print("\n3️⃣ RESEÑAS EN LA BASE DE DATOS:")
resenas = Resena.objects.all()
print(f"   Total reseñas: {resenas.count()}")

if resenas.count() > 0:
    print("\n   Detalles de reseñas:")
    for r in resenas:
        print(f"\n   Reseña ID {r.id}:")
        print(f"   - usuario_id: {r.usuario_id}")
        print(f"   - producto_id: {r.producto_id}")
        print(f"   - calificacion: {r.calificacion}")
        
        # Verificar si el usuario existe
        try:
            usuario = Usuario.objects.get(id=r.usuario_id)
            print(f"   - Usuario EXISTE: {usuario.email}")
        except Usuario.DoesNotExist:
            print(f"   - ⚠️ Usuario NO EXISTE (huérfana)")
        
        # Verificar si el producto existe
        try:
            producto = Producto.objects.get(id=r.producto_id)
            print(f"   - Producto EXISTE: {producto.nombre}")
        except Producto.DoesNotExist:
            print(f"   - ⚠️ Producto NO EXISTE (huérfana)")

print("\n" + "=" * 80)
print("SOLUCIÓN:")
print("=" * 80)

if resenas.count() > 0:
    print("\n⚠️ HAY RESEÑAS EN LA BASE DE DATOS")
    print("\nPara eliminar TODAS las reseñas y empezar limpio, ejecuta:")
    print("   python manage.py shell -c \"from apps.resenas.models import Resena; Resena.objects.all().delete(); print('Reseñas eliminadas')\"")
else:
    print("\n✅ No hay reseñas. La base de datos está limpia.")

print("\n" + "=" * 80)
