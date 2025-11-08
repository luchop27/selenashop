#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import Categoria, Coleccion

print("=" * 60)
print("PRUEBA: CREAR NUEVA SUBCATEGORÍA")
print("=" * 60)

try:
    # Buscar la categoría padre "Ropa"
    ropa = Categoria.objects.get(nombre="Ropa")
    print(f"\n✅ Categoría padre encontrada: {ropa.nombre} (ID: {ropa.id})")
    
    # Intentar crear una nueva subcategoría
    nueva_categoria = Categoria(
        nombre="Prueba Subcategoría",
        slug="prueba-subcategoria",
        descripcion="Esta es una prueba",
        padre=ropa,
        coleccion=ropa.coleccion,
        estado=True
    )
    
    print("\n🔄 Intentando guardar la nueva subcategoría...")
    nueva_categoria.save()
    print(f"✅ Subcategoría creada exitosamente! ID: {nueva_categoria.id}")
    
    # Eliminarla inmediatamente para no dejar datos de prueba
    print("\n🗑️  Eliminando subcategoría de prueba...")
    nueva_categoria.delete()
    print("✅ Subcategoría de prueba eliminada")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
