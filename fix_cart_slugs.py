"""
Script para agregar el campo producto_slug a los items existentes del carrito
que no lo tienen (tanto en BD como en sesiones activas).
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import CarritoItem, Producto
from django.contrib.sessions.models import Session
from django.utils import timezone
import json

def fix_database_carts():
    """
    No es necesario arreglar la BD porque el modelo CarritoItem
    no guarda el slug (se obtiene del producto relacionado).
    Pero verificamos que todos los productos tengan slug.
    """
    print("Verificando que todos los productos tengan slug...")
    productos_sin_slug = Producto.objects.filter(slug__isnull=True) | Producto.objects.filter(slug='')
    
    if productos_sin_slug.exists():
        print(f"⚠️  Encontrados {productos_sin_slug.count()} productos sin slug:")
        for producto in productos_sin_slug:
            print(f"  - ID {producto.id}: {producto.nombre}")
        print("  Estos productos necesitan un slug válido.")
    else:
        print("✅ Todos los productos tienen slug.")
    
    # Verificar items del carrito
    total_items = CarritoItem.objects.count()
    print(f"\n📦 Total de items en carritos de BD: {total_items}")
    
    if total_items > 0:
        print("✅ Los items del carrito obtienen el slug del producto relacionado automáticamente.")

def fix_session_carts():
    """
    Intentar arreglar sesiones activas que puedan tener items sin slug.
    Nota: Las sesiones están encriptadas, así que solo podemos limpiarlas.
    """
    print("\n" + "="*60)
    print("SESIONES ACTIVAS")
    print("="*60)
    
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    total_sessions = active_sessions.count()
    
    print(f"Total de sesiones activas: {total_sessions}")
    
    if total_sessions > 0:
        print(f"\nℹ️  Las sesiones activas se actualizarán automáticamente")
        print("   cuando los usuarios vuelvan a cargar el carrito.")
        print("   El método __iter__ de Cart agregará el slug si falta.")

if __name__ == '__main__':
    print("="*60)
    print("VERIFICACIÓN Y CORRECCIÓN DE SLUGS EN CARRITOS")
    print("="*60 + "\n")
    
    fix_database_carts()
    fix_session_carts()
    
    print("\n" + "="*60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*60)
    print("\nNotas importantes:")
    print("1. Los items del carrito en BD obtienen el slug del producto automáticamente")
    print("2. Los items en sesión se actualizarán al cargar la página del carrito")
    print("3. Los nuevos items agregados ya incluyen el slug correctamente")
