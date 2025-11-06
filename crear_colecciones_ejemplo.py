# Script para crear colecciones de ejemplo
from apps.productos.models import Coleccion
from django.utils.text import slugify

# Crear colecciones
colecciones_data = [
    {
        'nombre': 'Primavera 2024',
        'descripcion': 'Colección fresca y vibrante para la temporada de primavera',
        'posicion': 1,
        'destacada': True,
    },
    {
        'nombre': 'Verano Casual',
        'descripcion': 'Looks relajados y cómodos para el verano',
        'posicion': 2,
        'destacada': True,
    },
    {
        'nombre': 'Formal Elegante',
        'descripcion': 'Piezas sofisticadas para ocasiones especiales',
        'posicion': 3,
        'destacada': False,
    },
    {
        'nombre': 'Deportivo Activo',
        'descripcion': 'Ropa y accesorios para tu estilo de vida activo',
        'posicion': 4,
        'destacada': False,
    },
    {
        'nombre': 'Otoño Clásico',
        'descripcion': 'Colores cálidos y texturas acogedoras',
        'posicion': 5,
        'destacada': False,
    },
]

print("Creando colecciones de ejemplo...")
creadas = 0

for data in colecciones_data:
    slug = slugify(data['nombre'])
    coleccion, created = Coleccion.objects.get_or_create(
        slug=slug,
        defaults={
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'posicion': data['posicion'],
            'destacada': data['destacada'],
            'activo': True,
        }
    )
    
    if created:
        print(f"✓ Colección creada: {coleccion.nombre}")
        creadas += 1
    else:
        print(f"○ Colección ya existe: {coleccion.nombre}")

print(f"\n✅ Proceso completado. {creadas} colecciones creadas.")
print(f"Total de colecciones en la base de datos: {Coleccion.objects.count()}")

# Mostrar resumen
print("\n📋 COLECCIONES DISPONIBLES:")
for col in Coleccion.objects.all().order_by('posicion'):
    destacada = "⭐ DESTACADA" if col.destacada else ""
    print(f"  {col.posicion}. {col.nombre} {destacada}")
    print(f"     Slug: {col.slug}")
    print(f"     Categorías asociadas: {col.categorias.count()}")
