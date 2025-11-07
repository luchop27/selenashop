import os
import sys
import django

# Configurar Django
sys.path.insert(0, r'd:\Proyectos_Django_Trabajos\TiendaOnline\selenashop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from django.test import RequestFactory
from apps.productos.views import panel_productos_list
from apps.productos.models import Coleccion

print("\n" + "="*70)
print("TEST: Verificar contexto de la vista panel_productos_list")
print("="*70)

# Crear una request simulada
factory = RequestFactory()
request = factory.get('/admin-panel/products/')

# Llamar a la vista
from django.http import HttpRequest
response = panel_productos_list(request)

# Verificar el contexto
print(f"\nStatus code: {response.status_code}")
print(f"Template usado: {response.template_name if hasattr(response, 'template_name') else 'N/A'}")

# Obtener el contexto
context = response.context_data if hasattr(response, 'context_data') else {}

print(f"\nVariables en el contexto:")
print("-" * 70)
for key in context.keys():
    value = context[key]
    if key == 'colecciones_disponibles':
        print(f"\n✓ {key}:")
        if hasattr(value, '__iter__') and not isinstance(value, str):
            print(f"  Tipo: {type(value)}")
            print(f"  Count: {value.count() if hasattr(value, 'count') else len(list(value))}")
            for item in value:
                print(f"    - {item.nombre} (slug: {item.slug}, activo: {item.activo})")
        else:
            print(f"  Valor: {value}")
    else:
        print(f"  {key}: {type(value).__name__}")

# Verificar directamente desde la BD
print("\n" + "="*70)
print("VERIFICACIÓN DIRECTA EN LA BASE DE DATOS")
print("="*70)

colecciones = Coleccion.objects.filter(activo=True).order_by('nombre')
print(f"\nColecciones activas en BD: {colecciones.count()}")
for col in colecciones:
    print(f"  - {col.nombre} (slug: {col.slug})")

print("\n" + "="*70)
