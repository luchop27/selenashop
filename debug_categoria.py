#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import Categoria, Producto

# Buscar la categoría "traje de baño"
categorias = Categoria.objects.filter(nombre__icontains='traje')

print("=" * 60)
print("DIAGNÓSTICO DE CATEGORÍA 'TRAJE DE BAÑO'")
print("=" * 60)

for cat in categorias:
    print(f"\n📁 Categoría: {cat.nombre} (ID: {cat.id})")
    print(f"   Slug: {cat.slug}")
    print(f"   Padre: {cat.padre}")
    print(f"   Colección: {cat.coleccion}")
    print(f"   Estado: {cat.estado}")
    
    # Verificar productos relacionados
    productos = Producto.objects.filter(categoria=cat)
    print(f"\n   📦 Productos relacionados: {productos.count()}")
    for prod in productos:
        print(f"      - {prod.nombre} (ID: {prod.id})")
    
    # Verificar subcategorías
    subcats = cat.subcategorias.all()
    print(f"\n   📂 Subcategorías: {subcats.count()}")
    for subcat in subcats:
        print(f"      - {subcat.nombre} (ID: {subcat.id})")
    
    # Intentar ver si hay algún error al acceder a sus campos
    try:
        print(f"\n   🔍 Verificación de integridad:")
        print(f"      - created_at: {cat.created_at}")
        print(f"      - updated_at: {cat.updated_at}")
        print(f"      - posicion: {cat.posicion}")
        print(f"      - tipo: {cat.tipo if hasattr(cat, 'tipo') else 'N/A'}")
        if cat.imagen:
            print(f"      - imagen: {cat.imagen.url}")
        else:
            print(f"      - imagen: Sin imagen")
    except Exception as e:
        print(f"      ❌ ERROR al acceder a campos: {e}")

print("\n" + "=" * 60)
print("DIAGNÓSTICO COMPLETO")
print("=" * 60)
