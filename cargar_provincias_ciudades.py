#!/usr/bin/env python
"""
Script para cargar todas las provincias y ciudades (cantones) del Ecuador
a la base de datos Django.
Soporta tildes y ñ correctamente.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.usuarios.models import Provincia, Ciudad

# Datos de provincias con sus ciudades (cantones)
DATOS_ECUADOR = {
    'Azuay': [
        'Cuenca',
        'Girón',
        'Gualaceo',
        'Chordeleg',
        'Oña',
        'Paute',
        'Pucará',
        'San Fernando',
        'Santa Isabel',
        'Sígsig',
        'Nabón',
        'El Pan',
        'Sevilla de Oro'
    ],
    'Bolívar': [
        'Guaranda',
        'Caluma',
        'Chillanes',
        'Echeandía',
        'San Miguel',
        'Salinas'
    ],
    'Cañar': [
        'Azogues',
        'Bibián',
        'Cañar',
        'La Troncal',
        'El Tambo',
        'Déleg',
        'Suscal'
    ],
    'Carchi': [
        'Tulcán',
        'Bolívar',
        'Espejo',
        'Montúfar',
        'San Pedro de Huaca',
        'Mira'
    ],
    'Chimborazo': [
        'Riobamba',
        'Alausí',
        'Chunchi',
        'Colta',
        'Guamote',
        'Guano',
        'Cumandá',
        'Penipe',
        'Chambo'
    ],
    'Cotopaxi': [
        'Latacunga',
        'La Maná',
        'Pangua',
        'Pujilí',
        'Salcedo',
        'Saquisilí',
        'Sigchos'
    ],
    'El Oro': [
        'Machala',
        'Arenillas',
        'Atahualpa',
        'Balsas',
        'Chala',
        'Chilla',
        'El Guabo',
        'Huaquillas',
        'Piñas',
        'Portovelo',
        'Santa Rosa',
        'Zaruma',
        'Las Lajas',
        'Pasaje'
    ],
    'Esmeraldas': [
        'Esmeraldas',
        'Atacames',
        'Eloy Alfaro',
        'Muisne',
        'Quinindé',
        'Ríoverde',
        'San Lorenzo'
    ],
    'Galápagos': [
        'San Cristóbal',
        'Isabela',
        'Santa Cruz'
    ],
    'Guayas': [
        'Guayaquil',
        'Balao',
        'Balzar',
        'Colimes',
        'Daule',
        'Durán',
        'El Empalme',
        'El Triunfo',
        'Milagro',
        'Nobol',
        'Palestina',
        'Pedro Carbo',
        'Salinas',
        'Samborondón',
        'Santa Elena',
        'Santa Lucía',
        'Simón Bolívar',
        'Baba',
        'Vinces',
        'Yaguachi',
        'General Villamil Playas'
    ],
    'Imbabura': [
        'Ibarra',
        'Atuntaqui',
        'Cotacachi',
        'Otavalo',
        'Urcuquí',
        'Pimampiro',
        'San Miguel de Urcuquí',
        'Ambuquí'
    ],
    'Loja': [
        'Loja',
        'Catamayo',
        'Celica',
        'Chaguarpamba',
        'Espíndola',
        'Gonzanamá',
        'Macará',
        'Paltas',
        'Pindal',
        'Saraguro',
        'Sozoranga',
        'Zapotillo'
    ],
    'Los Ríos': [
        'Babahoyo',
        'Baba',
        'Bolívar',
        'Buena Fe',
        'Jipijapa',
        'Montecristi',
        'Paján',
        'Tosagua',
        'Calceta',
        'Rocafuerte',
        'San Juan',
        'Manta',
        'Pichincha',
        'Puerto López',
        'Puerto Viejo',
        'Santa Ana'
    ],
    'Manabí': [
        'Portoviejo',
        'Chone',
        'El Carmen',
        'Jipijapa',
        'Manta',
        'Montecristi',
        'Paján',
        'Pichincha',
        'Puerto López',
        'Puerto Viejo',
        'Santa Ana',
        'Tosagua',
        'Calceta',
        'Rocafuerte',
        'Sucre',
        '24 de Mayo',
        'Olmedo',
        'Pedernales',
        'Jaramijó',
        'Manta'
    ],
    'Morona Santiago': [
        'Macas',
        'Alausí',
        'Chunchi',
        'Guamote',
        'Colta',
        'Penipe',
        'Riobamba',
        'Santiago',
        'Sucúa',
        'Tena',
        'Palora',
        'Méndez',
        'San Juan Bosco',
        'Gualaquiza',
        'Limón Indanza',
        'Taisha',
        'Achuar'
    ],
    'Napo': [
        'Tena',
        'Archidona',
        'Carlos Julio Arosemena Tola',
        'Quijos',
        'Baeza'
    ],
    'Orellana': [
        'Francisco de Orellana',
        'Aguarico',
        'La Joya de los Sachas'
    ],
    'Pastaza': [
        'Puyo',
        'Arajuno',
        'Mera',
        'Santa Clara'
    ],
    'Pichincha': [
        'Quito',
        'Cayambe',
        'Machachi',
        'Mejía',
        'Rumiñahui',
        'San Miguel de los Bancos',
        'Santo Domingo',
        'La Concordia',
        'Pedro Moncayo',
        'Quito',
        'Nanegalito',
        'Sangolquí'
    ],
    'Santa Elena': [
        'Santa Elena',
        'La Libertad',
        'Salinas'
    ],
    'Santo Domingo': [
        'Santo Domingo',
        'La Concordia'
    ],
    'Sucumbíos': [
        'Nueva Loja',
        'Cascales',
        'Cuyabeno',
        'González Suárez',
        'Lago Agrio',
        'Putumayo',
        'Shushufindi',
        'Carcén'
    ],
    'Tungurahua': [
        'Ambato',
        'Baños',
        'Cevallos',
        'Latacunga',
        'Mocha',
        'Patate',
        'Pelileo',
        'Píllaro',
        'Quero',
        'Tisaleo',
        'Tena'
    ],
    'Zamora Chinchipe': [
        'Zamora',
        'Chinchipe',
        'El Pangui',
        'Guacamayos',
        'Izumi',
        'Nangaritza',
        'Palandá',
        'Paquisha',
        'Yantzaza',
        'Centinela del Cóndor'
    ]
}


def cargar_datos():
    """Carga todas las provincias y ciudades en la base de datos"""
    
    print("Iniciando carga de provincias y ciudades del Ecuador...")
    print("-" * 60)
    
    provincias_creadas = 0
    ciudades_creadas = 0
    ciudades_existentes = 0
    
    for nombre_provincia, ciudades_list in DATOS_ECUADOR.items():
        try:
            # Crear o obtener provincia
            provincia, creada = Provincia.objects.get_or_create(
                nombre=nombre_provincia,
                defaults={'activa': True}
            )
            
            if creada:
                provincias_creadas += 1
                print(f"✅ Provincia creada: {nombre_provincia}")
            else:
                print(f"ℹ️  Provincia existente: {nombre_provincia}")
            
            # Crear ciudades (cantones) de la provincia
            for nombre_ciudad in ciudades_list:
                ciudad, creada = Ciudad.objects.get_or_create(
                    nombre=nombre_ciudad,
                    provincia=provincia,
                    defaults={'activa': True}
                )
                
                if creada:
                    ciudades_creadas += 1
                    print(f"   └─ ✅ Ciudad creada: {nombre_ciudad}")
                else:
                    ciudades_existentes += 1
                    print(f"   └─ ℹ️  Ciudad existente: {nombre_ciudad}")
        
        except Exception as e:
            print(f"❌ Error procesando provincia {nombre_provincia}: {str(e)}")
    
    print("-" * 60)
    print(f"✅ Carga completada:")
    print(f"   • Provincias: {provincias_creadas} creadas")
    print(f"   • Ciudades: {ciudades_creadas} creadas, {ciudades_existentes} ya existentes")
    total_ciudades = ciudades_creadas + ciudades_existentes
    print(f"   • Total de ciudades: {total_ciudades}")
    print("-" * 60)


if __name__ == '__main__':
    cargar_datos()
