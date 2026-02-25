# apps/productos/image_processor.py
"""
Procesador de imágenes para convertir formatos no compatibles con navegadores
como HEIC (iPhone) a formatos web estándar como JPEG.
"""
import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import pillow_heif


def convert_heic_to_jpeg(image_field):
    """
    Convierte una imagen HEIC a JPEG manteniendo la calidad original.
    
    Args:
        image_field: Campo ImageField de Django
        
    Returns:
        InMemoryUploadedFile con la imagen convertida a JPEG
    """
    # Registrar el plugin HEIF
    pillow_heif.register_heif_opener()
    
    # Obtener la extensión del archivo
    file_name = image_field.name
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Solo procesar si es HEIC o HEIF
    if file_ext not in ['.heic', '.heif']:
        return image_field
    
    try:
        # Abrir la imagen HEIC
        img = Image.open(image_field)
        
        # Convertir a RGB si es necesario (HEIC puede tener canal alpha)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco para imágenes con transparencia
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Crear buffer para la imagen JPEG
        output = BytesIO()
        
        # Guardar como JPEG con máxima calidad (sin compresión)
        img.save(
            output,
            format='JPEG',
            quality=100,  # Máxima calidad
            optimize=False,  # No optimizar (mantener tamaño original)
            subsampling=0  # Sin subsampling (mejor calidad)
        )
        output.seek(0)
        
        # Crear nuevo nombre de archivo con extensión .jpg
        new_file_name = os.path.splitext(file_name)[0] + '.jpg'
        
        # Crear InMemoryUploadedFile
        return InMemoryUploadedFile(
            output,
            'ImageField',
            new_file_name,
            'image/jpeg',
            output.tell(),
            None
        )
        
    except Exception as e:
        # Si hay algún error, devolver el archivo original
        print(f"Error al convertir HEIC a JPEG: {e}")
        return image_field


def process_uploaded_image(image_field):
    """
    Procesa una imagen subida, convirtiéndola si es necesario.
    
    Args:
        image_field: Campo ImageField de Django
        
    Returns:
        Imagen procesada (convertida si era HEIC, original si no)
    """
    if not image_field:
        return None
    
    file_ext = os.path.splitext(image_field.name)[1].lower()
    
    # Convertir HEIC/HEIF a JPEG para compatibilidad web
    if file_ext in ['.heic', '.heif']:
        return convert_heic_to_jpeg(image_field)
    
    # Para otros formatos, devolver sin cambios (sin compresión)
    return image_field
