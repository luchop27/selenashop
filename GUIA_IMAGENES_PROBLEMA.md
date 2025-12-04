# SOLUCIONES PARA IMÁGENES NO VISIBLES EN DJANGO

## ✅ CHECKLIST - VERIFICA ESTO PRIMERO:

### 1. ¿Está corriendo el servidor de desarrollo?
   - Debes ejecutar: `python manage.py runserver`
   - Las imágenes SOLO se sirven en desarrollo con `DEBUG=True`

### 2. Verifica que Django sirve los media files
   Tu `urls.py` debe tener esto (YA LO TIENES):
   ```python
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

### 3. Revisa el panel admin
   - Ve a: http://localhost:8000/admin/
   - Abre el modelo que contiene las imágenes (ej: AboutUsImage, Producto, etc)
   - Busca una imagen que hayas cargado
   - Copia la URL que aparece en el campo y pruébala en el navegador
   - Ejemplo: `/media/about-us/nombre-imagen.jpg`

### 4. Verifica la carpeta media
   La carpeta `media/` debe tener este contenido:
   ```
   media/
   ├── about-us/        (imágenes del about-us)
   ├── categorias/      (imágenes de categorías)
   ├── colecciones/     (imágenes de colecciones)
   └── productos/       (imágenes de productos)
   ```

### 5. Revisa los permisos de carpeta
   En Windows, la carpeta `media/` debe tener permisos de lectura.
   Haz clic derecho en carpeta → Propiedades → Seguridad

## ❌ PROBLEMA: Las imágenes están en la BD pero no en la carpeta media

SOLUCIÓN: Las imágenes se cargaron pero algo eliminó los archivos.
- Vuelve a subir las imágenes desde el admin
- Verifica que hay espacio en disco

## ❌ PROBLEMA: El servidor no reconoce /media/

SOLUCIÓN: Reinicia el servidor Django:
```bash
# Detén el servidor (Ctrl+C)
# Ejecuta:
python manage.py runserver
```

## ❌ PROBLEMA: Sigue sin funcionar

EJECUTA ESTE SCRIPT EN LA TERMINAL:
```bash
python manage.py shell
```

Luego en el shell de Python:
```python
from django.conf import settings
from pathlib import Path

print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"Existe media/: {Path(settings.MEDIA_ROOT).exists()}")

# Ver carpetas dentro de media
for item in Path(settings.MEDIA_ROOT).iterdir():
    print(f"  - {item.name}")
```

Si no ves carpetas, necesitas hacer un `collectstatic`:
```bash
python manage.py collectstatic
```

## 🔧 CONFIGURACIÓN CORRECTA EN settings.py

Verifica que tienes esto (YA LO TIENES BIEN):
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 📝 EN LAS TEMPLATES

Para mostrar imágenes, usa:
```django
<!-- Para imágenes de media (subidas por usuario) -->
<img src="{{ objeto.imagen.url }}" alt="...">

<!-- Para imágenes estáticas -->
<img src="{% static 'images/archivo.jpg' %}" alt="...">
```

## 🚀 SOLUCIÓN RÁPIDA SI NADA FUNCIONA

1. Elimina la carpeta `media/` completa
2. Crea una nueva carpeta vacía llamada `media/`
3. Reinicia Django: `python manage.py runserver`
4. Ve al admin y sube UNA imagen de prueba
5. Recarga la página donde debería verse
6. Si aparece, el problema está en los archivos antiguos

## 📊 PRODUCCIÓN (no es tu caso, pero para referencia)

En producción, debes servir media files con:
- Nginx
- Apache
- Whitenoise (para Heroku, etc)
- O un CDN

Para desarrollo, Django se encarga automáticamente con DEBUG=True.
