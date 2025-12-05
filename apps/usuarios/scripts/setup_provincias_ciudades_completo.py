"""
Script completo para poblar provincias y ciudades del Ecuador en la base de datos
Ejecutar: python manage.py shell < apps/usuarios/scripts/setup_provincias_ciudades_completo.py
"""

from apps.usuarios.models import Provincia, Ciudad

# Datos de provincias y sus ciudades (cantones)
datos_provincias_ciudades = {
    'Azuay': [
        'Cuenca', 'Gualaceo', 'Paute', 'Sígsig', 'El Pan', 'Pucará'
    ],
    'Bolívar': [
        'Guaranda', 'Caluma', 'Chillanes', 'Echeandia', 'San Miguel', 'Barreiro', 'Simiatug'
    ],
    'Cañar': [
        'Azogues', 'La Troncal', 'Cañar'
    ],
    'Carchi': [
        'Tulcán', 'Bolívar', 'San Gabriel', 'Montúfar', 'Espejo', 'Mira'
    ],
    'Chimborazo': [
        'Riobamba', 'Ambato', 'Baños', 'Guaranda', 'Latacunga', 'Pallatanga', 'Cumandá', 'Colta', 'Chambo', 'Penipe'
    ],
    'Cotopaxi': [
        'Latacunga', 'La Maná', 'Pangua', 'Salcedo', 'Saquisilí', 'Sigchos', 'Pujilí'
    ],
    'El Oro': [
        'Machala', 'Arenillas', 'Atahualpa', 'Balsas', 'Chilla', 'El Guabo', 'Huaquillas', 'Las Lajas', 'Marchena', 'Pasaje', 'Piñas', 'Portovelo', 'Santa Rosa', 'Zaruma'
    ],
    'Esmeraldas': [
        'Esmeraldas', 'Atacames', 'Manta', 'Rioverde', 'Quinindé', 'San Lorenzo', 'Eloy Alfaro'
    ],
    'Guayas': [
        'Guayaquil', 'Duran', 'Samborondon', 'Daule', 'Milagro', 'Naranjito', 'Nobol', 'Playas', 'Santa Lucia', 'Salinas', 'General Antonio Elizalde', 'Balzar', 'El Triunfo', 'Simón Bolívar', 'Yaguachi'
    ],
    'Imbabura': [
        'Ibarra', 'Otavalo', 'Urcuquí', 'Antonio Ante', 'Cotacachi', 'Pimampiro'
    ],
    'Loja': [
        'Loja', 'Catamayo', 'Macará', 'Calvas', 'Celica', 'Chaguarpamba', 'Espíndola', 'Gonzanamá', 'Jimbura', 'Paltas', 'Pindal', 'Puyango', 'Saraguro', 'Sozoranga', 'Quilanga', 'Olmedo'
    ],
    'Los Ríos': [
        'Babahoyo', 'Quevedo', 'Vinces', 'Ventanas', 'Baba', 'Buena Fe', 'Urdaneta', 'Pueblo Viejo', 'Mocache', 'Montalvo', 'Palenque', 'Pimocha', 'Samborondón'
    ],
    'Manabí': [
        'Portoviejo', 'Manta', 'Bahía de Caráquez', 'Jipijapa', 'Chone', 'El Carmen', 'Junín', 'Rocafuerte', 'Tosagua', 'Calceta', 'Sucre', 'Motecristi', 'Santa Ana', 'Montecristi', 'Puerto López', 'Olmedo', 'Paján', 'Pichincha', 'San Vicente', 'Pedernales', 'Jaramijó', 'Coddelí'
    ],
    'Morona Santiago': [
        'Macas', 'Sucúa', 'Limon', 'Palora', 'Santiago', 'Tiwintza', 'Gualaquiza', 'Morona', 'Logroño', 'San Juan Bosco', 'Taisha', 'Huamboya'
    ],
    'Napo': [
        'Tena', 'Archidona', 'Quijos', 'Puyo', 'Carlos Julio Arosemena Tola'
    ],
    'Orellana': [
        'Puerto Francisco de Orellana', 'Aguarico', 'La Joya de los Sachas', 'Loreto', 'Taracoa'
    ],
    'Pastaza': [
        'Puyo', 'Mera', 'Santa Clara', 'Arajuno'
    ],
    'Pichincha': [
        'Quito', 'Cayambe', 'Machachi', 'Sangolquí', 'Tambillo', 'Rumiñahui', 'Pedro Moncayo', 'Pedro Vicente Maldonado'
    ],
    'Santa Elena': [
        'Santa Elena', 'La Libertad', 'Salinas'
    ],
    'Santo Domingo de los Tsáchilas': [
        'Santo Domingo'
    ],
    'Sucumbíos': [
        'Nueva Loja', 'Gonzalo Pizarro', 'Cascales', 'Cuyabeno', 'Putumayo', 'Shushufindi', 'Tetete'
    ],
    'Tungurahua': [
        'Ambato', 'Baños', 'Latacunga', 'Pelileo', 'Píllaro', 'Patate', 'Mocha', 'Quero', 'Tisaleo'
    ]
}

print("=" * 60)
print("Iniciando poblamiendo de Provincias y Ciudades")
print("=" * 60)

# Primero, crear todas las provincias
provincias_creadas = {}
print("\n1. Creando provincias...")
print("-" * 60)

for nombre_provincia in datos_provincias_ciudades.keys():
    provincia, created = Provincia.objects.get_or_create(
        nombre=nombre_provincia,
        defaults={'activa': True}
    )
    provincias_creadas[nombre_provincia] = provincia
    if created:
        print(f"✓ Creada provincia: {nombre_provincia}")
    else:
        print(f"- Provincia ya existe: {nombre_provincia}")

print(f"\nTotal de provincias: {Provincia.objects.count()}")

# Ahora, crear todas las ciudades relacionadas a sus provincias
print("\n2. Creando ciudades/cantones...")
print("-" * 60)

contador_ciudades = 0
for nombre_provincia, ciudades_lista in datos_provincias_ciudades.items():
    provincia = provincias_creadas[nombre_provincia]
    print(f"\n{nombre_provincia}: {len(ciudades_lista)} cantones")
    
    for ciudad_nombre in ciudades_lista:
        ciudad, created = Ciudad.objects.get_or_create(
            nombre=ciudad_nombre,
            provincia=provincia,
            defaults={'activa': True}
        )
        if created:
            print(f"  ✓ {ciudad_nombre}")
            contador_ciudades += 1
        else:
            print(f"  - {ciudad_nombre} (ya existe)")

print("\n" + "=" * 60)
print(f"✓ Total de ciudades en la BD: {Ciudad.objects.count()}")
print(f"✓ Total de provincias en la BD: {Provincia.objects.count()}")
print("=" * 60)
print("¡Importación completada exitosamente!")
