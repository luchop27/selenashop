"""
Script para poblar las ciudades del Ecuador en la base de datos
Ejecutar: python manage.py shell < apps/usuarios/scripts/populate_ciudades.py
"""

from apps.usuarios.models import Ciudad

# Lista de ciudades del Ecuador por provincia
ciudades_ecuador = [
    # Azuay
    {'nombre': 'Cuenca', 'provincia': 'Azuay', 'codigo_postal': '010101'},
    {'nombre': 'Gualaceo', 'provincia': 'Azuay', 'codigo_postal': '010102'},
    {'nombre': 'Paute', 'provincia': 'Azuay', 'codigo_postal': '010103'},
    {'nombre': 'Sígsig', 'provincia': 'Azuay', 'codigo_postal': '010104'},
    
    # Bolívar
    {'nombre': 'Guaranda', 'provincia': 'Bolívar', 'codigo_postal': '020101'},
    {'nombre': 'Caluma', 'provincia': 'Bolívar', 'codigo_postal': '020102'},
    {'nombre': 'Chillanes', 'provincia': 'Bolívar', 'codigo_postal': '020103'},
    
    # Cañar
    {'nombre': 'Azogues', 'provincia': 'Cañar', 'codigo_postal': '030101'},
    {'nombre': 'La Troncal', 'provincia': 'Cañar', 'codigo_postal': '030102'},
    {'nombre': 'Cañar', 'provincia': 'Cañar', 'codigo_postal': '030103'},
    
    # Carchi
    {'nombre': 'Tulcán', 'provincia': 'Carchi', 'codigo_postal': '040101'},
    {'nombre': 'Ibarra', 'provincia': 'Carchi', 'codigo_postal': '040102'},
    {'nombre': 'San Gabriel', 'provincia': 'Carchi', 'codigo_postal': '040103'},
    
    # Chimborazo
    {'nombre': 'Riobamba', 'provincia': 'Chimborazo', 'codigo_postal': '050101'},
    {'nombre': 'Guaranda', 'provincia': 'Chimborazo', 'codigo_postal': '050102'},
    {'nombre': 'Latacunga', 'provincia': 'Chimborazo', 'codigo_postal': '050103'},
    
    # Cotopaxi
    {'nombre': 'Latacunga', 'provincia': 'Cotopaxi', 'codigo_postal': '050101'},
    {'nombre': 'Ambato', 'provincia': 'Cotopaxi', 'codigo_postal': '050102'},
    {'nombre': 'Salcedo', 'provincia': 'Cotopaxi', 'codigo_postal': '050103'},
    
    # El Oro
    {'nombre': 'Machala', 'provincia': 'El Oro', 'codigo_postal': '070101'},
    {'nombre': 'Santa Rosa', 'provincia': 'El Oro', 'codigo_postal': '070102'},
    {'nombre': 'Huaquillas', 'provincia': 'El Oro', 'codigo_postal': '070103'},
    
    # Esmeraldas
    {'nombre': 'Esmeraldas', 'provincia': 'Esmeraldas', 'codigo_postal': '080101'},
    {'nombre': 'Atacames', 'provincia': 'Esmeraldas', 'codigo_postal': '080102'},
    {'nombre': 'Manta', 'provincia': 'Esmeraldas', 'codigo_postal': '080103'},
    
    # Guayas
    {'nombre': 'Guayaquil', 'provincia': 'Guayas', 'codigo_postal': '090101'},
    {'nombre': 'Durán', 'provincia': 'Guayas', 'codigo_postal': '090102'},
    {'nombre': 'Samborondón', 'provincia': 'Guayas', 'codigo_postal': '090103'},
    {'nombre': 'Daule', 'provincia': 'Guayas', 'codigo_postal': '090104'},
    {'nombre': 'Milagro', 'provincia': 'Guayas', 'codigo_postal': '090105'},
    
    # Imbabura
    {'nombre': 'Ibarra', 'provincia': 'Imbabura', 'codigo_postal': '100101'},
    {'nombre': 'Otavalo', 'provincia': 'Imbabura', 'codigo_postal': '100102'},
    {'nombre': 'Antonio Ante', 'provincia': 'Imbabura', 'codigo_postal': '100103'},
    
    # Loja
    {'nombre': 'Loja', 'provincia': 'Loja', 'codigo_postal': '110101'},
    {'nombre': 'Catamayo', 'provincia': 'Loja', 'codigo_postal': '110102'},
    {'nombre': 'Macará', 'provincia': 'Loja', 'codigo_postal': '110103'},
    
    # Los Ríos
    {'nombre': 'Babahoyo', 'provincia': 'Los Ríos', 'codigo_postal': '120101'},
    {'nombre': 'Quevedo', 'provincia': 'Los Ríos', 'codigo_postal': '120102'},
    {'nombre': 'Vinces', 'provincia': 'Los Ríos', 'codigo_postal': '120103'},
    
    # Manabí
    {'nombre': 'Manta', 'provincia': 'Manabí', 'codigo_postal': '130101'},
    {'nombre': 'Portoviejo', 'provincia': 'Manabí', 'codigo_postal': '130102'},
    {'nombre': 'Bahía de Caráquez', 'provincia': 'Manabí', 'codigo_postal': '130103'},
    {'nombre': 'Jipijapa', 'provincia': 'Manabí', 'codigo_postal': '130104'},
    
    # Morona Santiago
    {'nombre': 'Macas', 'provincia': 'Morona Santiago', 'codigo_postal': '140101'},
    {'nombre': 'Sucúa', 'provincia': 'Morona Santiago', 'codigo_postal': '140102'},
    {'nombre': 'Palora', 'provincia': 'Morona Santiago', 'codigo_postal': '140103'},
    
    # Napo
    {'nombre': 'Tena', 'provincia': 'Napo', 'codigo_postal': '150101'},
    {'nombre': 'Archidona', 'provincia': 'Napo', 'codigo_postal': '150102'},
    {'nombre': 'Puyo', 'provincia': 'Napo', 'codigo_postal': '150103'},
    
    # Pastaza
    {'nombre': 'Puyo', 'provincia': 'Pastaza', 'codigo_postal': '160101'},
    {'nombre': 'Mera', 'provincia': 'Pastaza', 'codigo_postal': '160102'},
    {'nombre': 'Santa Clara', 'provincia': 'Pastaza', 'codigo_postal': '160103'},
    
    # Pichincha
    {'nombre': 'Quito', 'provincia': 'Pichincha', 'codigo_postal': '170101'},
    {'nombre': 'Cayambe', 'provincia': 'Pichincha', 'codigo_postal': '170102'},
    {'nombre': 'Latacunga', 'provincia': 'Pichincha', 'codigo_postal': '170103'},
    {'nombre': 'Machachi', 'provincia': 'Pichincha', 'codigo_postal': '170104'},
    {'nombre': 'Sangolquí', 'provincia': 'Pichincha', 'codigo_postal': '170105'},
    
    # Santa Elena
    {'nombre': 'Santa Elena', 'provincia': 'Santa Elena', 'codigo_postal': '240101'},
    {'nombre': 'La Libertad', 'provincia': 'Santa Elena', 'codigo_postal': '240102'},
    {'nombre': 'Salinas', 'provincia': 'Santa Elena', 'codigo_postal': '240103'},
    
    # Santo Domingo
    {'nombre': 'Santo Domingo', 'provincia': 'Santo Domingo de los Tsáchilas', 'codigo_postal': '230101'},
    
    # Sucumbíos
    {'nombre': 'Nueva Loja', 'provincia': 'Sucumbíos', 'codigo_postal': '210101'},
    {'nombre': 'El Coca', 'provincia': 'Sucumbíos', 'codigo_postal': '210102'},
    {'nombre': 'Lago Agrio', 'provincia': 'Sucumbíos', 'codigo_postal': '210103'},
    
    # Tungurahua
    {'nombre': 'Ambato', 'provincia': 'Tungurahua', 'codigo_postal': '180101'},
    {'nombre': 'Latacunga', 'provincia': 'Tungurahua', 'codigo_postal': '180102'},
    {'nombre': 'Baños', 'provincia': 'Tungurahua', 'codigo_postal': '180103'},
    
    # Orellana
    {'nombre': 'Puerto Francisco de Orellana', 'provincia': 'Orellana', 'codigo_postal': '220101'},
    {'nombre': 'Coca', 'provincia': 'Orellana', 'codigo_postal': '220102'},
]

# Eliminar duplicados y crear/actualizar ciudades
print("Importando ciudades del Ecuador...")

for ciudad_data in ciudades_ecuador:
    ciudad, created = Ciudad.objects.get_or_create(
        nombre=ciudad_data['nombre'],
        defaults={
            'provincia': ciudad_data['provincia'],
            'codigo_postal': ciudad_data['codigo_postal'],
            'activa': True
        }
    )
    if created:
        print(f"✓ Creada: {ciudad.nombre}")
    else:
        print(f"- Existe: {ciudad.nombre}")

total = Ciudad.objects.count()
print(f"\nTotal de ciudades en la base de datos: {total}")
print("¡Importación completada!")
