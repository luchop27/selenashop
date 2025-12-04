#!/usr/bin/env python
"""
Script para poblar provincias y ciudades del Ecuador
Ejecutar: python manage.py shell < setup_provincias_ciudades.py
"""

from apps.usuarios.models import Provincia, Ciudad

# Datos de provincias y sus ciudades
provincias_ciudades = {
    'Azuay': ['Cuenca', 'Gualaceo', 'Paute', 'Sígsig', 'Chordeleg'],
    'Bolívar': ['Guaranda', 'Caluma', 'Chillanes', 'Echeandía', 'San Miguel'],
    'Cañar': ['Azogues', 'La Troncal', 'Cañar', 'El Tambo', 'Biblián'],
    'Carchi': ['Tulcán', 'San Gabriel', 'Espejo', 'Montúfar', 'Huaca'],
    'Chimborazo': ['Riobamba', 'Latacunga', 'Penipe', 'Guamote', 'Cumandá'],
    'Cotopaxi': ['Latacunga', 'La Maná', 'Pangua', 'Salcedo', 'Pujilí'],
    'El Oro': ['Machala', 'Santa Rosa', 'Huaquillas', 'Pasaje', 'Piñas'],
    'Esmeraldas': ['Esmeraldas', 'Atacames', 'Muisne', 'Quinindé', 'San Lorenzo'],
    'Guayas': ['Guayaquil', 'Durán', 'Milagro', 'Daule', 'Samborondón', 'Balzar'],
    'Imbabura': ['Ibarra', 'Otavalo', 'Antonio Ante', 'Cotacachi', 'Urcuquí'],
    'Loja': ['Loja', 'Catamayo', 'Macará', 'Vilcabamba', 'Saraguro'],
    'Los Ríos': ['Babahoyo', 'Quevedo', 'Vinces', 'Baba', 'Mocache'],
    'Manabí': ['Manta', 'Portoviejo', 'Jipijapa', 'El Carmen', 'Chone', 'Bahía de Caráquez'],
    'Morona Santiago': ['Macas', 'Sucúa', 'Palora', 'Tena', 'Puyo'],
    'Napo': ['Tena', 'Archidona', 'Puerto Misahuallí', 'Puyo', 'Quijos'],
    'Pastaza': ['Puyo', 'Mera', 'Santa Clara', 'Arajuno', 'Shell'],
    'Pichincha': ['Quito', 'Cayambe', 'Machachi', 'Sangolquí', 'Latacunga', 'Puembo'],
    'Santa Elena': ['Santa Elena', 'La Libertad', 'Salinas', 'Olón', 'Manglaralto'],
    'Santo Domingo': ['Santo Domingo'],
    'Sucumbíos': ['Nueva Loja', 'Lago Agrio', 'Cascales', 'Putumayo', 'Cuyabeno'],
    'Tungurahua': ['Ambato', 'Baños', 'Latacunga', 'Pelileo', 'Píllaro'],
    'Orellana': ['Puerto Francisco de Orellana', 'Coca', 'Joya de los Sachas', 'Loreto'],
}

print("\n" + "="*70)
print("POBLANDO PROVINCIAS Y CIUDADES DEL ECUADOR")
print("="*70)

total_provincias = 0
total_ciudades = 0

for provincia_nombre, ciudades_nombres in provincias_ciudades.items():
    # Crear provincia
    provincia, created = Provincia.objects.get_or_create(
        nombre=provincia_nombre,
        defaults={'activa': True}
    )
    
    if created:
        print(f"\n✓ Provincia creada: {provincia_nombre}")
        total_provincias += 1
    else:
        print(f"\n- Provincia existe: {provincia_nombre}")
    
    # Crear ciudades de la provincia
    for ciudad_nombre in ciudades_nombres:
        ciudad, created = Ciudad.objects.get_or_create(
            nombre=ciudad_nombre,
            provincia=provincia,
            defaults={'activa': True}
        )
        
        if created:
            print(f"  ✓ Ciudad: {ciudad_nombre}")
            total_ciudades += 1
        else:
            print(f"  - Ciudad existe: {ciudad_nombre}")

print("\n" + "="*70)
print(f"RESULTADO:")
print(f"  Total provincias creadas: {total_provincias}")
print(f"  Total ciudades creadas: {total_ciudades}")
print(f"  Provincias en BD: {Provincia.objects.count()}")
print(f"  Ciudades en BD: {Ciudad.objects.count()}")
print("="*70 + "\n")
