"""
Script para poblar las ciudades del Ecuador en la base de datos
Ejecutar: python manage.py shell < apps/usuarios/scripts/populate_ciudades.py
"""

from apps.usuarios.models import Ciudad

# Lista de ciudades del Ecuador por provincia - Completa con todos los cantones
ciudades_ecuador = [
    # AZUAY (6 cantones)
    {'nombre': 'Cuenca', 'provincia': 'Azuay', 'codigo_postal': '010101'},
    {'nombre': 'Gualaceo', 'provincia': 'Azuay', 'codigo_postal': '010102'},
    {'nombre': 'Paute', 'provincia': 'Azuay', 'codigo_postal': '010103'},
    {'nombre': 'Sígsig', 'provincia': 'Azuay', 'codigo_postal': '010104'},
    {'nombre': 'El Pan', 'provincia': 'Azuay', 'codigo_postal': '010105'},
    {'nombre': 'Pucará', 'provincia': 'Azuay', 'codigo_postal': '010106'},
    
    # BOLÍVAR (7 cantones)
    {'nombre': 'Guaranda', 'provincia': 'Bolívar', 'codigo_postal': '020101'},
    {'nombre': 'Caluma', 'provincia': 'Bolívar', 'codigo_postal': '020102'},
    {'nombre': 'Chillanes', 'provincia': 'Bolívar', 'codigo_postal': '020103'},
    {'nombre': 'Echeandia', 'provincia': 'Bolívar', 'codigo_postal': '020104'},
    {'nombre': 'San Miguel', 'provincia': 'Bolívar', 'codigo_postal': '020105'},
    {'nombre': 'Barreiro', 'provincia': 'Bolívar', 'codigo_postal': '020106'},
    {'nombre': 'Simiatug', 'provincia': 'Bolívar', 'codigo_postal': '020107'},
    
    # CAÑAR (3 cantones)
    {'nombre': 'Azogues', 'provincia': 'Cañar', 'codigo_postal': '030101'},
    {'nombre': 'La Troncal', 'provincia': 'Cañar', 'codigo_postal': '030102'},
    {'nombre': 'Cañar', 'provincia': 'Cañar', 'codigo_postal': '030103'},
    
    # CARCHI (6 cantones)
    {'nombre': 'Tulcán', 'provincia': 'Carchi', 'codigo_postal': '040101'},
    {'nombre': 'Bolívar', 'provincia': 'Carchi', 'codigo_postal': '040102'},
    {'nombre': 'San Gabriel', 'provincia': 'Carchi', 'codigo_postal': '040103'},
    {'nombre': 'Montúfar', 'provincia': 'Carchi', 'codigo_postal': '040104'},
    {'nombre': 'Espejo', 'provincia': 'Carchi', 'codigo_postal': '040105'},
    {'nombre': 'Mira', 'provincia': 'Carchi', 'codigo_postal': '040106'},
    
    # CHIMBORAZO (10 cantones)
    {'nombre': 'Riobamba', 'provincia': 'Chimborazo', 'codigo_postal': '050101'},
    {'nombre': 'Ambato', 'provincia': 'Chimborazo', 'codigo_postal': '050102'},
    {'nombre': 'Baños', 'provincia': 'Chimborazo', 'codigo_postal': '050103'},
    {'nombre': 'Guaranda', 'provincia': 'Chimborazo', 'codigo_postal': '050104'},
    {'nombre': 'Latacunga', 'provincia': 'Chimborazo', 'codigo_postal': '050105'},
    {'nombre': 'Pallatanga', 'provincia': 'Chimborazo', 'codigo_postal': '050106'},
    {'nombre': 'Cumandá', 'provincia': 'Chimborazo', 'codigo_postal': '050107'},
    {'nombre': 'Colta', 'provincia': 'Chimborazo', 'codigo_postal': '050108'},
    {'nombre': 'Chambo', 'provincia': 'Chimborazo', 'codigo_postal': '050109'},
    {'nombre': 'Penipe', 'provincia': 'Chimborazo', 'codigo_postal': '050110'},
    
    # COTOPAXI (7 cantones)
    {'nombre': 'Latacunga', 'provincia': 'Cotopaxi', 'codigo_postal': '050201'},
    {'nombre': 'La Maná', 'provincia': 'Cotopaxi', 'codigo_postal': '050202'},
    {'nombre': 'Pangua', 'provincia': 'Cotopaxi', 'codigo_postal': '050203'},
    {'nombre': 'Salcedo', 'provincia': 'Cotopaxi', 'codigo_postal': '050204'},
    {'nombre': 'Saquisilí', 'provincia': 'Cotopaxi', 'codigo_postal': '050205'},
    {'nombre': 'Sigchos', 'provincia': 'Cotopaxi', 'codigo_postal': '050206'},
    {'nombre': 'Pujilí', 'provincia': 'Cotopaxi', 'codigo_postal': '050207'},
    
    # EL ORO (14 cantones)
    {'nombre': 'Machala', 'provincia': 'El Oro', 'codigo_postal': '070101'},
    {'nombre': 'Arenillas', 'provincia': 'El Oro', 'codigo_postal': '070102'},
    {'nombre': 'Atahualpa', 'provincia': 'El Oro', 'codigo_postal': '070103'},
    {'nombre': 'Balsas', 'provincia': 'El Oro', 'codigo_postal': '070104'},
    {'nombre': 'Chilla', 'provincia': 'El Oro', 'codigo_postal': '070105'},
    {'nombre': 'El Guabo', 'provincia': 'El Oro', 'codigo_postal': '070106'},
    {'nombre': 'Huaquillas', 'provincia': 'El Oro', 'codigo_postal': '070107'},
    {'nombre': 'Las Lajas', 'provincia': 'El Oro', 'codigo_postal': '070108'},
    {'nombre': 'Marchena', 'provincia': 'El Oro', 'codigo_postal': '070109'},
    {'nombre': 'Pasaje', 'provincia': 'El Oro', 'codigo_postal': '070110'},
    {'nombre': 'Piñas', 'provincia': 'El Oro', 'codigo_postal': '070111'},
    {'nombre': 'Portovelo', 'provincia': 'El Oro', 'codigo_postal': '070112'},
    {'nombre': 'Santa Rosa', 'provincia': 'El Oro', 'codigo_postal': '070113'},
    {'nombre': 'Zaruma', 'provincia': 'El Oro', 'codigo_postal': '070114'},
    
    # ESMERALDAS (7 cantones)
    {'nombre': 'Esmeraldas', 'provincia': 'Esmeraldas', 'codigo_postal': '080101'},
    {'nombre': 'Atacames', 'provincia': 'Esmeraldas', 'codigo_postal': '080102'},
    {'nombre': 'Manta', 'provincia': 'Esmeraldas', 'codigo_postal': '080103'},
    {'nombre': 'Rioverde', 'provincia': 'Esmeraldas', 'codigo_postal': '080104'},
    {'nombre': 'Quinindé', 'provincia': 'Esmeraldas', 'codigo_postal': '080105'},
    {'nombre': 'San Lorenzo', 'provincia': 'Esmeraldas', 'codigo_postal': '080106'},
    {'nombre': 'Eloy Alfaro', 'provincia': 'Esmeraldas', 'codigo_postal': '080107'},
    
    # GUAYAS (15 cantones)
    {'nombre': 'Guayaquil', 'provincia': 'Guayas', 'codigo_postal': '090101'},
    {'nombre': 'Duran', 'provincia': 'Guayas', 'codigo_postal': '090102'},
    {'nombre': 'Samborondon', 'provincia': 'Guayas', 'codigo_postal': '090103'},
    {'nombre': 'Daule', 'provincia': 'Guayas', 'codigo_postal': '090104'},
    {'nombre': 'Milagro', 'provincia': 'Guayas', 'codigo_postal': '090105'},
    {'nombre': 'Naranjito', 'provincia': 'Guayas', 'codigo_postal': '090106'},
    {'nombre': 'Nobol', 'provincia': 'Guayas', 'codigo_postal': '090107'},
    {'nombre': 'Playas', 'provincia': 'Guayas', 'codigo_postal': '090108'},
    {'nombre': 'Santa Lucia', 'provincia': 'Guayas', 'codigo_postal': '090109'},
    {'nombre': 'Salinas', 'provincia': 'Guayas', 'codigo_postal': '090110'},
    {'nombre': 'General Antonio Elizalde', 'provincia': 'Guayas', 'codigo_postal': '090111'},
    {'nombre': 'Balzar', 'provincia': 'Guayas', 'codigo_postal': '090112'},
    {'nombre': 'El Triunfo', 'provincia': 'Guayas', 'codigo_postal': '090113'},
    {'nombre': 'Simón Bolívar', 'provincia': 'Guayas', 'codigo_postal': '090114'},
    {'nombre': 'Yaguachi', 'provincia': 'Guayas', 'codigo_postal': '090115'},
    
    # IMBABURA (6 cantones)
    {'nombre': 'Ibarra', 'provincia': 'Imbabura', 'codigo_postal': '100101'},
    {'nombre': 'Otavalo', 'provincia': 'Imbabura', 'codigo_postal': '100102'},
    {'nombre': 'Urcuquí', 'provincia': 'Imbabura', 'codigo_postal': '100103'},
    {'nombre': 'Antonio Ante', 'provincia': 'Imbabura', 'codigo_postal': '100104'},
    {'nombre': 'Cotacachi', 'provincia': 'Imbabura', 'codigo_postal': '100105'},
    {'nombre': 'Pimampiro', 'provincia': 'Imbabura', 'codigo_postal': '100106'},
    
    # LOJA (16 cantones)
    {'nombre': 'Loja', 'provincia': 'Loja', 'codigo_postal': '110101'},
    {'nombre': 'Catamayo', 'provincia': 'Loja', 'codigo_postal': '110102'},
    {'nombre': 'Macará', 'provincia': 'Loja', 'codigo_postal': '110103'},
    {'nombre': 'Calvas', 'provincia': 'Loja', 'codigo_postal': '110104'},
    {'nombre': 'Celica', 'provincia': 'Loja', 'codigo_postal': '110105'},
    {'nombre': 'Chaguarpamba', 'provincia': 'Loja', 'codigo_postal': '110106'},
    {'nombre': 'Espíndola', 'provincia': 'Loja', 'codigo_postal': '110107'},
    {'nombre': 'Gonzanamá', 'provincia': 'Loja', 'codigo_postal': '110108'},
    {'nombre': 'Jimbura', 'provincia': 'Loja', 'codigo_postal': '110109'},
    {'nombre': 'Paltas', 'provincia': 'Loja', 'codigo_postal': '110110'},
    {'nombre': 'Pindal', 'provincia': 'Loja', 'codigo_postal': '110111'},
    {'nombre': 'Puyango', 'provincia': 'Loja', 'codigo_postal': '110112'},
    {'nombre': 'Saraguro', 'provincia': 'Loja', 'codigo_postal': '110113'},
    {'nombre': 'Sozoranga', 'provincia': 'Loja', 'codigo_postal': '110114'},
    {'nombre': 'Quilanga', 'provincia': 'Loja', 'codigo_postal': '110115'},
    {'nombre': 'Olmedo', 'provincia': 'Loja', 'codigo_postal': '110116'},
    
    # LOS RÍOS (13 cantones)
    {'nombre': 'Babahoyo', 'provincia': 'Los Ríos', 'codigo_postal': '120101'},
    {'nombre': 'Quevedo', 'provincia': 'Los Ríos', 'codigo_postal': '120102'},
    {'nombre': 'Vinces', 'provincia': 'Los Ríos', 'codigo_postal': '120103'},
    {'nombre': 'Ventanas', 'provincia': 'Los Ríos', 'codigo_postal': '120104'},
    {'nombre': 'Baba', 'provincia': 'Los Ríos', 'codigo_postal': '120105'},
    {'nombre': 'Buena Fe', 'provincia': 'Los Ríos', 'codigo_postal': '120106'},
    {'nombre': 'Urdaneta', 'provincia': 'Los Ríos', 'codigo_postal': '120107'},
    {'nombre': 'Pueblo Viejo', 'provincia': 'Los Ríos', 'codigo_postal': '120108'},
    {'nombre': 'Mocache', 'provincia': 'Los Ríos', 'codigo_postal': '120109'},
    {'nombre': 'Montalvo', 'provincia': 'Los Ríos', 'codigo_postal': '120110'},
    {'nombre': 'Palenque', 'provincia': 'Los Ríos', 'codigo_postal': '120111'},
    {'nombre': 'Pimocha', 'provincia': 'Los Ríos', 'codigo_postal': '120112'},
    {'nombre': 'Samborondón', 'provincia': 'Los Ríos', 'codigo_postal': '120113'},
    
    # MANABÍ (22 cantones)
    {'nombre': 'Portoviejo', 'provincia': 'Manabí', 'codigo_postal': '130101'},
    {'nombre': 'Manta', 'provincia': 'Manabí', 'codigo_postal': '130102'},
    {'nombre': 'Bahía de Caráquez', 'provincia': 'Manabí', 'codigo_postal': '130103'},
    {'nombre': 'Jipijapa', 'provincia': 'Manabí', 'codigo_postal': '130104'},
    {'nombre': 'Chone', 'provincia': 'Manabí', 'codigo_postal': '130105'},
    {'nombre': 'El Carmen', 'provincia': 'Manabí', 'codigo_postal': '130106'},
    {'nombre': 'Junín', 'provincia': 'Manabí', 'codigo_postal': '130107'},
    {'nombre': 'Rocafuerte', 'provincia': 'Manabí', 'codigo_postal': '130108'},
    {'nombre': 'Tosagua', 'provincia': 'Manabí', 'codigo_postal': '130109'},
    {'nombre': 'Calceta', 'provincia': 'Manabí', 'codigo_postal': '130110'},
    {'nombre': 'Sucre', 'provincia': 'Manabí', 'codigo_postal': '130111'},
    {'nombre': 'Motecristi', 'provincia': 'Manabí', 'codigo_postal': '130112'},
    {'nombre': 'Santa Ana', 'provincia': 'Manabí', 'codigo_postal': '130113'},
    {'nombre': 'Montecristi', 'provincia': 'Manabí', 'codigo_postal': '130114'},
    {'nombre': 'Puerto López', 'provincia': 'Manabí', 'codigo_postal': '130115'},
    {'nombre': 'Olmedo', 'provincia': 'Manabí', 'codigo_postal': '130116'},
    {'nombre': 'Paján', 'provincia': 'Manabí', 'codigo_postal': '130117'},
    {'nombre': 'Pichincha', 'provincia': 'Manabí', 'codigo_postal': '130118'},
    {'nombre': 'San Vicente', 'provincia': 'Manabí', 'codigo_postal': '130119'},
    {'nombre': 'Pedernales', 'provincia': 'Manabí', 'codigo_postal': '130120'},
    {'nombre': 'Jaramijó', 'provincia': 'Manabí', 'codigo_postal': '130121'},
    {'nombre': 'Coddelí', 'provincia': 'Manabí', 'codigo_postal': '130122'},
    
    # MORONA SANTIAGO (12 cantones)
    {'nombre': 'Macas', 'provincia': 'Morona Santiago', 'codigo_postal': '140101'},
    {'nombre': 'Sucúa', 'provincia': 'Morona Santiago', 'codigo_postal': '140102'},
    {'nombre': 'Limon', 'provincia': 'Morona Santiago', 'codigo_postal': '140103'},
    {'nombre': 'Palora', 'provincia': 'Morona Santiago', 'codigo_postal': '140104'},
    {'nombre': 'Santiago', 'provincia': 'Morona Santiago', 'codigo_postal': '140105'},
    {'nombre': 'Tiwintza', 'provincia': 'Morona Santiago', 'codigo_postal': '140106'},
    {'nombre': 'Gualaquiza', 'provincia': 'Morona Santiago', 'codigo_postal': '140107'},
    {'nombre': 'Morona', 'provincia': 'Morona Santiago', 'codigo_postal': '140108'},
    {'nombre': 'Logroño', 'provincia': 'Morona Santiago', 'codigo_postal': '140109'},
    {'nombre': 'San Juan Bosco', 'provincia': 'Morona Santiago', 'codigo_postal': '140110'},
    {'nombre': 'Taisha', 'provincia': 'Morona Santiago', 'codigo_postal': '140111'},
    {'nombre': 'Huamboya', 'provincia': 'Morona Santiago', 'codigo_postal': '140112'},
    
    # NAPO (5 cantones)
    {'nombre': 'Tena', 'provincia': 'Napo', 'codigo_postal': '150101'},
    {'nombre': 'Archidona', 'provincia': 'Napo', 'codigo_postal': '150102'},
    {'nombre': 'Quijos', 'provincia': 'Napo', 'codigo_postal': '150103'},
    {'nombre': 'Puyo', 'provincia': 'Napo', 'codigo_postal': '150104'},
    {'nombre': 'Carlos Julio Arosemena Tola', 'provincia': 'Napo', 'codigo_postal': '150105'},
    
    # ORELLANA (5 cantones)
    {'nombre': 'Puerto Francisco de Orellana', 'provincia': 'Orellana', 'codigo_postal': '220101'},
    {'nombre': 'Aguarico', 'provincia': 'Orellana', 'codigo_postal': '220102'},
    {'nombre': 'La Joya de los Sachas', 'provincia': 'Orellana', 'codigo_postal': '220103'},
    {'nombre': 'Loreto', 'provincia': 'Orellana', 'codigo_postal': '220104'},
    {'nombre': 'Taracoa', 'provincia': 'Orellana', 'codigo_postal': '220105'},
    
    # PASTAZA (4 cantones)
    {'nombre': 'Puyo', 'provincia': 'Pastaza', 'codigo_postal': '160101'},
    {'nombre': 'Mera', 'provincia': 'Pastaza', 'codigo_postal': '160102'},
    {'nombre': 'Santa Clara', 'provincia': 'Pastaza', 'codigo_postal': '160103'},
    {'nombre': 'Arajuno', 'provincia': 'Pastaza', 'codigo_postal': '160104'},
    
    # PICHINCHA (8 cantones)
    {'nombre': 'Quito', 'provincia': 'Pichincha', 'codigo_postal': '170101'},
    {'nombre': 'Cayambe', 'provincia': 'Pichincha', 'codigo_postal': '170102'},
    {'nombre': 'Machachi', 'provincia': 'Pichincha', 'codigo_postal': '170103'},
    {'nombre': 'Sangolquí', 'provincia': 'Pichincha', 'codigo_postal': '170104'},
    {'nombre': 'Tambillo', 'provincia': 'Pichincha', 'codigo_postal': '170105'},
    {'nombre': 'Rumiñahui', 'provincia': 'Pichincha', 'codigo_postal': '170106'},
    {'nombre': 'Pedro Moncayo', 'provincia': 'Pichincha', 'codigo_postal': '170107'},
    {'nombre': 'Pedro Vicente Maldonado', 'provincia': 'Pichincha', 'codigo_postal': '170108'},
    
    # SANTA ELENA (3 cantones)
    {'nombre': 'Santa Elena', 'provincia': 'Santa Elena', 'codigo_postal': '240101'},
    {'nombre': 'La Libertad', 'provincia': 'Santa Elena', 'codigo_postal': '240102'},
    {'nombre': 'Salinas', 'provincia': 'Santa Elena', 'codigo_postal': '240103'},
    
    # SANTO DOMINGO (1 cantón)
    {'nombre': 'Santo Domingo', 'provincia': 'Santo Domingo de los Tsáchilas', 'codigo_postal': '230101'},
    
    # SUCUMBÍOS (7 cantones)
    {'nombre': 'Nueva Loja', 'provincia': 'Sucumbíos', 'codigo_postal': '210101'},
    {'nombre': 'Gonzalo Pizarro', 'provincia': 'Sucumbíos', 'codigo_postal': '210102'},
    {'nombre': 'Cascales', 'provincia': 'Sucumbíos', 'codigo_postal': '210103'},
    {'nombre': 'Cuyabeno', 'provincia': 'Sucumbíos', 'codigo_postal': '210104'},
    {'nombre': 'Putumayo', 'provincia': 'Sucumbíos', 'codigo_postal': '210105'},
    {'nombre': 'Shushufindi', 'provincia': 'Sucumbíos', 'codigo_postal': '210106'},
    {'nombre': 'Tetete', 'provincia': 'Sucumbíos', 'codigo_postal': '210107'},
    
    # TUNGURAHUA (9 cantones)
    {'nombre': 'Ambato', 'provincia': 'Tungurahua', 'codigo_postal': '180101'},
    {'nombre': 'Baños', 'provincia': 'Tungurahua', 'codigo_postal': '180102'},
    {'nombre': 'Latacunga', 'provincia': 'Tungurahua', 'codigo_postal': '180103'},
    {'nombre': 'Pelileo', 'provincia': 'Tungurahua', 'codigo_postal': '180104'},
    {'nombre': 'Píllaro', 'provincia': 'Tungurahua', 'codigo_postal': '180105'},
    {'nombre': 'Patate', 'provincia': 'Tungurahua', 'codigo_postal': '180106'},
    {'nombre': 'Mocha', 'provincia': 'Tungurahua', 'codigo_postal': '180107'},
    {'nombre': 'Quero', 'provincia': 'Tungurahua', 'codigo_postal': '180108'},
    {'nombre': 'Tisaleo', 'provincia': 'Tungurahua', 'codigo_postal': '180109'},
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
