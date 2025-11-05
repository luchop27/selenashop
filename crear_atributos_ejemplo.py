"""
Script para crear atributos de ejemplo en la base de datos.
Ejecutar con: python manage.py shell < crear_atributos_ejemplo.py
"""

from apps.productos.models import Atributo, ValorAtributo
from django.utils.text import slugify

# Limpiar datos anteriores (opcional)
print("Limpiando datos anteriores...")
ValorAtributo.objects.all().delete()
Atributo.objects.all().delete()

# ===== ATRIBUTO: COLOR =====
print("Creando atributo: Color")
color = Atributo.objects.create(
    nombre="Color",
    slug="color",
    tipo="color",
    descripcion="Colores disponibles para los productos",
    activo=True,
    posicion=1
)

# Valores de Color
colores = [
    ("Rojo", "#FF0000"),
    ("Azul", "#0000FF"),
    ("Verde", "#00FF00"),
    ("Negro", "#000000"),
    ("Blanco", "#FFFFFF"),
    ("Rosa", "#FFC0CB"),
    ("Amarillo", "#FFFF00"),
    ("Naranja", "#FFA500"),
    ("Morado", "#800080"),
    ("Gris", "#808080"),
]

for i, (nombre, codigo) in enumerate(colores, 1):
    ValorAtributo.objects.create(
        atributo=color,
        valor=nombre,
        codigo_color=codigo,
        posicion=i,
        activo=True
    )
    print(f"  ✓ {nombre} ({codigo})")

# ===== ATRIBUTO: TALLA =====
print("\nCreando atributo: Talla")
talla = Atributo.objects.create(
    nombre="Talla",
    slug="talla",
    tipo="talla",
    descripcion="Tallas de ropa disponibles",
    activo=True,
    posicion=2
)

# Valores de Talla
tallas = ["XS", "S", "M", "L", "XL", "XXL"]
for i, nombre in enumerate(tallas, 1):
    ValorAtributo.objects.create(
        atributo=talla,
        valor=nombre,
        posicion=i,
        activo=True
    )
    print(f"  ✓ {nombre}")

# ===== ATRIBUTO: MARCA =====
print("\nCreando atributo: Marca")
marca = Atributo.objects.create(
    nombre="Marca",
    slug="marca",
    tipo="texto",
    descripcion="Marcas de los productos",
    activo=True,
    posicion=3
)

# Valores de Marca
marcas = ["Zara", "H&M", "Nike", "Adidas", "Gucci", "Prada", "Chanel", "Dior"]
for i, nombre in enumerate(marcas, 1):
    ValorAtributo.objects.create(
        atributo=marca,
        valor=nombre,
        posicion=i,
        activo=True
    )
    print(f"  ✓ {nombre}")

# ===== ATRIBUTO: MATERIAL =====
print("\nCreando atributo: Material")
material = Atributo.objects.create(
    nombre="Material",
    slug="material",
    tipo="texto",
    descripcion="Materiales de fabricación",
    activo=True,
    posicion=4
)

# Valores de Material
materiales = ["Algodón", "Poliéster", "Seda", "Lana", "Cuero", "Lino", "Denim"]
for i, nombre in enumerate(materiales, 1):
    ValorAtributo.objects.create(
        atributo=material,
        valor=nombre,
        posicion=i,
        activo=True
    )
    print(f"  ✓ {nombre}")

# ===== ATRIBUTO: ESTILO =====
print("\nCreando atributo: Estilo")
estilo_attr = Atributo.objects.create(
    nombre="Estilo",
    slug="estilo",
    tipo="texto",
    descripcion="Estilos de moda",
    activo=True,
    posicion=5
)

# Valores de Estilo
estilos = ["Casual", "Formal", "Deportivo", "Elegante", "Vintage", "Moderno"]
for i, nombre in enumerate(estilos, 1):
    ValorAtributo.objects.create(
        atributo=estilo_attr,
        valor=nombre,
        posicion=i,
        activo=True
    )
    print(f"  ✓ {nombre}")

print("\n✅ ¡Atributos creados exitosamente!")
print(f"Total atributos: {Atributo.objects.count()}")
print(f"Total valores: {ValorAtributo.objects.count()}")
