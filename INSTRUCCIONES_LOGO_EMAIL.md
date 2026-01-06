# Problema: Logo no se muestra en emails

## Causa del Problema
El logo en base64 es demasiado grande (130KB = 174,470 caracteres en base64). 
Muchos clientes de email (Gmail, Outlook, Yahoo) bloquean imágenes base64 grandes por:
- Seguridad (prevenir malware)
- Rendimiento (emails muy pesados)
- Limitaciones de tamaño de HTML

## Soluciones

### Solución 1: Usar URL Pública del Logo (RECOMENDADA)
Subir el logo a un servicio de hosting de imágenes gratuito:

**Opciones de hosting:**
1. **ImgBB** (https://imgbb.com/) - Gratuito, sin registro
2. **Imgur** (https://imgur.com/) - Requiere cuenta
3. **Cloudinary** (https://cloudinary.com/) - CDN profesional, plan gratuito
4. **Tu propio servidor** - Subir a tu hosting web

**Pasos:**
1. Ir a https://imgbb.com/
2. Subir `static/images/logo/logoselena.png`
3. Copiar la URL directa de la imagen
4. Actualizar el código con la URL pública

### Solución 2: Reducir tamaño del logo
Comprimir la imagen a ~20KB:
- Usar herramientas online: TinyPNG, Compressor.io
- Reducir dimensiones si es muy grande
- Convertir a formato optimizado

### Solución 3: Usar CID (Content-ID) con adjuntos
Adjuntar el logo al email y referenciarlo con cid: en el HTML.
Más complejo pero más confiable.

## Implementación Temporal
Mientras tanto, usa una URL pública temporal o un logo más pequeño.
