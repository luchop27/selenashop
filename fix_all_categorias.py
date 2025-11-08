#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import Categoria

print("=" * 60)
print("REPARANDO TODAS LAS CATEGORÍAS CON CAMPOS NULL")
print("=" * 60)

# Obtener todas las categorías
categorias = Categoria.objects.all()

reparadas = 0
for cat in categorias:
    necesita_reparacion = False
    
    # Verificar campo posicion
    if not hasattr(cat, 'posicion') or cat.posicion is None:
        print(f"⚠️  {cat.nombre} (ID: {cat.id}) - Campo 'posicion' es NULL")
        cat.posicion = 0
        necesita_reparacion = True
    
    if necesita_reparacion:
        try:
            cat.save()
            print(f"   ✅ Reparada")
            reparadas += 1
        except Exception as e:
            print(f"   ❌ ERROR al reparar: {e}")

print("\n" + "=" * 60)
print(f"RESUMEN: {reparadas} categorías reparadas de {categorias.count()} totales")
print("=" * 60)
