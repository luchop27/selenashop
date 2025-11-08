#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import Categoria

# Buscar la categoría "traje de baño"
try:
    cat = Categoria.objects.get(id=6)
    print(f"✅ Categoría encontrada: {cat.nombre} (ID: {cat.id})")
    
    # Intentar agregar el campo posicion si no existe
    if not hasattr(cat, 'posicion') or cat.posicion is None:
        print("⚠️  Campo 'posicion' no existe o es NULL")
        cat.posicion = 0
        cat.save()
        print("✅ Campo 'posicion' agregado con valor 0")
    
    # Verificar otros campos que puedan faltar
    if not hasattr(cat, 'tipo') or cat.tipo is None:
        print("⚠️  Campo 'tipo' no existe o es NULL")
        # No hacer nada si el campo no existe en el modelo
    
    print("\n🔍 Verificando integridad después del fix:")
    cat.refresh_from_db()
    print(f"   - nombre: {cat.nombre}")
    print(f"   - slug: {cat.slug}")
    print(f"   - padre: {cat.padre}")
    print(f"   - posicion: {cat.posicion if hasattr(cat, 'posicion') else 'N/A'}")
    print(f"   - estado: {cat.estado}")
    
    print("\n✅ Categoría reparada exitosamente!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
