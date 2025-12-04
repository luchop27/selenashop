# 🔧 SOLUCIÓN: IMÁGENES NO SE MUESTRAN EN DJANGO

## Lo que ya está bien ✅
Tu configuración de Django es correcta:
- `settings.py` tiene MEDIA_URL y MEDIA_ROOT configurados
- `urls.py` sirve los media files en desarrollo
- La carpeta `media/` existe

## PASOS PARA SOLUCIONAR:

### 1️⃣ REINICIA EL SERVIDOR
Esto es lo más importante - las URLs de media se cargan cuando Django inicia:
```bash
# En la terminal, detén el servidor actual (Ctrl+C)
# Luego ejecuta:
python manage.py runserver
```

### 2️⃣ VERIFICA EN EL NAVEGADOR
Ve a `http://localhost:8000/` y abre el **Inspector de Elementos** (F12)
- Tab "Network" 
- Busca las solicitudes a `/media/`
- Si ves error 404, significa que Django NO está sirviendo media files
- Si ves 200, las imágenes se encuentran pero algo más está mal

### 3️⃣ PRUEBA UNA IMAGEN DIRECTAMENTE
Ve a la URL del navegador: `http://localhost:8000/media/about-us/[nombre-de-archivo]`
- Si ves la imagen: Django SÍ sirve media files
- Si ves 404: Las imágenes no están en la carpeta `media/`

### 4️⃣ VERIFICA EL ADMIN
Ve a `http://localhost:8000/admin/core/aboutusimage/`
- Haz clic en una imagen
- En el campo "Imagen" copia el nombre/ruta
- Verifica que el archivo existe en `media/` con ese nombre

### 5️⃣ SI SEGUÍA SIN FUNCIONAR - REINSTALA PILLOW
Las imágenes requieren la librería Pillow:
```bash
pip install --upgrade Pillow
python manage.py runserver
```

### 6️⃣ ÚLTIMO RECURSO - RESETEA MEDIA
```bash
# 1. Detén Django (Ctrl+C)
# 2. Elimina carpeta media:
rmdir /s media
# 3. Crea nueva carpeta media vacía:
mkdir media
# 4. Crea subcarpetas:
mkdir media/about-us
mkdir media/categorias
mkdir media/colecciones
mkdir media/productos
# 5. Reinicia Django:
python manage.py runserver
```

## 📝 CAMBIOS REALIZADOS
He actualizado `selenashop/urls.py` para agregar una ruta explícita para media files.

## ✅ VERIFICA QUE FUNCIONA
1. Sube una imagen desde el admin
2. Recarga la página
3. Deberías ver la imagen

Si aún tienes problemas, comparte:
- ¿Qué error ves en el Inspector de Elementos?
- ¿Qué URL intenta cargar?
- ¿Qué status HTTP (404, 200, etc)?
