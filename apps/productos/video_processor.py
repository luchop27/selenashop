"""
Procesador de videos para eliminar audio automáticamente
Mantiene la resolución y calidad original del video
"""
import os
import subprocess
import tempfile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO


def remove_audio_from_video(video_field):
    """
    Elimina el audio de un video manteniendo la calidad y resolución original.
    
    Args:
        video_field: Campo de archivo de video (FileField)
    
    Returns:
        InMemoryUploadedFile: Video sin audio
    """
    # Obtener extensión del archivo
    file_name = video_field.name
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Crear archivo temporal para el video original
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_input:
        # Escribir el video original al archivo temporal
        for chunk in video_field.chunks():
            temp_input.write(chunk)
        temp_input_path = temp_input.name
    
    # Crear archivo temporal para el video sin audio
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
    temp_output_path = temp_output.name
    temp_output.close()
    
    try:
        # Comando FFmpeg para copiar video sin recodificar y eliminar audio
        # -c:v copy: copia el stream de video sin recodificar (mantiene calidad)
        # -an: elimina todas las pistas de audio
        command = [
            'ffmpeg',
            '-i', temp_input_path,      # Input file
            '-c:v', 'copy',              # Copiar video sin recodificar
            '-an',                       # Eliminar audio
            '-y',                        # Sobrescribir archivo de salida
            temp_output_path             # Output file
        ]
        
        # Ejecutar FFmpeg
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # Leer el video procesado
        with open(temp_output_path, 'rb') as f:
            video_data = f.read()
        
        # Crear nuevo archivo Django
        video_io = BytesIO(video_data)
        
        # Generar nombre para el archivo procesado
        base_name = os.path.splitext(file_name)[0]
        new_name = f"{base_name}_sin_audio{file_ext}"
        
        # Crear InMemoryUploadedFile
        new_video = InMemoryUploadedFile(
            video_io,
            None,
            new_name,
            video_field.content_type,
            len(video_data),
            None
        )
        
        return new_video
        
    except subprocess.CalledProcessError as e:
        # Si FFmpeg falla, devolver el video original sin modificar
        print(f"Error procesando video: {e.stderr.decode()}")
        video_field.seek(0)
        return video_field
        
    except FileNotFoundError:
        # Si FFmpeg no está instalado, devolver el video original
        print("FFmpeg no está instalado. El video se subirá con audio.")
        video_field.seek(0)
        return video_field
        
    finally:
        # Limpiar archivos temporales
        try:
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)
        except:
            pass


def process_uploaded_video(video_field):
    """
    Procesa un video subido eliminando el audio.
    
    Args:
        video_field: Campo de archivo de video
    
    Returns:
        Video procesado sin audio o video original si hay error
    """
    if not video_field:
        return video_field
    
    return remove_audio_from_video(video_field)
