# 📖 Sistema Dinámico de Páginas de Ayuda

## Resumen de lo que se implementó

Se ha creado un **sistema completo y dinámico** para gestionar las páginas de ayuda de SelenaShop (Términos y Condiciones, Política de Privacidad, Devoluciones y Envíos) directamente desde el **Admin de Django**.

## ¿Cómo funciona?

### 1. **Nueva App: `apps.ayudas`**
Se creó una nueva aplicación Django que contiene:
- **Modelo `PaginaAyuda`**: Almacena el contenido de cada página
- **Admin**: Interface para editar el contenido
- **Vistas**: Sirven el contenido dinámicamente

### 2. **Datos Disponibles**

Las páginas de ayuda se dividen en 4 tipos:

| Tipo | Nombre | URL |
|------|--------|-----|
| `terminos` | Términos y Condiciones | `/términos-condiciones/` |
| `privacidad` | Política de Privacidad | `/politica-privacidad/` |
| `devoluciones` | Devoluciones y Cambios | `/devoluciones-cambios/` |
| `envios` | Envíos y Entregas | `/envios/` |

### 3. **Template Unificado**
El archivo `templates/terms-conditions.html` se usa como template único para todas las páginas. Carga dinámicamente:
- ✅ **Título** desde la base de datos
- ✅ **Contenido HTML** desde la base de datos
- ✅ Cambios automáticos según la página visitada

## 📱 Cómo Usar

### Acceder al Admin

1. Ve a `http://localhost:8000/admin/`
2. Inicia sesión con tu cuenta de administrador
3. En el menú izquierdo, busca **"Páginas de Ayuda"** bajo la sección **"PÁGINAS DE AYUDA"**

### Editar una Página

1. Haz clic en el tipo de página que quieres editar (ej: "Términos y Condiciones")
2. Modifica el contenido en el campo de **Contenido**
3. Puedes usar **HTML básico** para formatear (h4, p, ul, li, etc.)
4. Haz clic en **"Guardar"**

### Vista Previa

Después de guardar, ve a la URL correspondiente para ver tu contenido:
- `/términos-condiciones/`
- `/politica-privacidad/`
- `/devoluciones-cambios/`
- `/envios/`

## 💾 Contenido Inicial

Se han creado 4 páginas de ejemplo con contenido. Puedes editarlas en cualquier momento.

## 🎨 Formato de Contenido

Puedes usar HTML en el campo de contenido. Ejemplo:

```html
<div class="box">
    <h4>Mi Título</h4>
    <p>Mi párrafo con texto.</p>
    <ul style="margin-left: 20px;">
        <li>Punto 1</li>
        <li>Punto 2</li>
    </ul>
</div>

<div class="box">
    <h4>Otro Título</h4>
    <p>Otro párrafo.</p>
</div>
```

## 🔗 Enlaces en el Footer

Los enlaces en el footer (base.html) ya están configurados para usar las nuevas páginas:

- ✅ "Política de Privacidad" → `/politica-privacidad/`
- ✅ "Devoluciones y Cambios" → `/devoluciones-cambios/`
- ✅ "Envíos" → `/envios/`
- ✅ "Términos y Condiciones" → `/términos-condiciones/`

## 📝 Archivos Modificados/Creados

### Creados:
- `apps/ayudas/models.py` - Modelo de datos
- `apps/ayudas/admin.py` - Interface del admin
- `apps/ayudas/views.py` - Vistas
- `apps/ayudas/urls.py` - URLs
- `apps/ayudas/apps.py` - Configuración de la app
- `init_paginas_ayuda.py` - Script de inicialización

### Modificados:
- `selenashop/settings.py` - Agregada `apps.ayudas` a INSTALLED_APPS
- `selenashop/urls.py` - Agregadas rutas de ayudas
- `core/views.py` - Actualizadas vistas para usar el nuevo sistema
- `templates/terms-conditions.html` - Convertido a template dinámico

## 🚀 Ejemplos de Uso

### Crear Contenido Completamente Personalizado

En el Admin:
1. Edita "Términos y Condiciones"
2. Reemplaza el contenido con tu texto propio
3. Usa la etiqueta `|safe` en el template para permitir HTML

### Agregar Listas

```html
<div class="box">
    <h4>Opciones de Envío</h4>
    <ul style="margin-left: 20px;">
        <li><strong>Envío Estándar:</strong> 5-7 días - Gratis</li>
        <li><strong>Envío Expresado:</strong> 2-3 días - $10</li>
    </ul>
</div>
```

### Agregar Links

```html
<p>Para más información, <a href="https://ejemplo.com">haz clic aquí</a>.</p>
```

## ✅ Ventajas del Sistema

1. **Dinámico**: Cambios inmediatos sin tocar el código
2. **Escalable**: Fácil agregar más páginas de ayuda
3. **Admin Amigable**: Interface simple y clara
4. **Template Reutilizable**: Una sola plantilla para todo
5. **HTML Flexible**: Puedes diseñar como quieras

## ❌ Posibles Errores

### La página muestra "No hay contenido disponible"
- Verifica que en el Admin la página esté marcada como "Activo"
- Asegúrate de que el `tipo` coincida con el de la URL

### Los cambios no se ven
- Actualiza el navegador (Ctrl+F5)
- Verifica que hayas hecho clic en "Guardar" en el Admin

## 📞 Contacto y Soporte

Si tienes dudas sobre cómo editar el contenido, recuerda:
- El contenido se edita en el **Admin Django** (`/admin/`)
- Los cambios son **inmediatos**
- Puedes usar **HTML básico**
- No necesitas tocar código
