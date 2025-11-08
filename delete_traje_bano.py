#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import Categoria

print("=" * 60)
print("ELIMINANDO SUBCATEGORÍA 'TRAJE DE BAÑO'")
print("=" * 60)

try:
    cat = Categoria.objects.get(id=6)
    print(f"\n📁 Categoría encontrada:")
    print(f"   - ID: {cat.id}")
    print(f"   - Nombre: {cat.nombre}")
    print(f"   - Slug: {cat.slug}")
    print(f"   - Padre: {cat.padre}")
    print(f"   - Productos: {cat.productos.count()}")
    print(f"   - Subcategorías: {cat.subcategorias.count()}")
    
    # Confirmar eliminación
    respuesta = input("\n¿Estás seguro de eliminar esta categoría? (SI/NO): ")
    
    if respuesta.upper() == 'SI':
        nombre = cat.nombre
        cat.delete()
        print(f"\n✅ Categoría '{nombre}' eliminada exitosamente!")
    else:
        print("\n❌ Eliminación cancelada")
        
except Categoria.DoesNotExist:
    print("\n❌ La categoría no existe")
except Exception as e:
    print(f"\n❌ ERROR al eliminar: {e}")
    import traceback
    traceback.print_exc()
