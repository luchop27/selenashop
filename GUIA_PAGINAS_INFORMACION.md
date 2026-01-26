# Sistema Dinámico de Páginas de Información

## ¿Qué se hizo?

Se implementó un sistema flexible que permite gestionar todas las páginas de información (Términos y Condiciones, Política de Privacidad, Devoluciones y Cambios, Envíos) desde un único lugar en el admin de Django.

## Componentes Creados

### 1. Modelo: `InfoPage` (core/models.py)
```python
class InfoPage(models.Model):
    slug = CharField()  # terms-conditions, privacy-policy, delivery-return, shipping
    titulo = CharField()  # Título que aparece en la página
    contenido = TextField()  # Contenido HTML de la página
    seo_meta_description = CharField()  # Meta descripción para SEO
    activo = BooleanField()  # Mostrar/ocultar la página
```

### 2. Vistas Actualizadas (core/views.py)
- `info_page(request, slug)` - Vista principal que carga cualquier página por slug
- `terms_conditions()` - Redirige a `info_page(request, 'terms-conditions')`
- `privacy_policy()` - Redirige a `info_page(request, 'privacy-policy')`
- `delivery_return()` - Redirige a `info_page(request, 'delivery-return')`
- `shipping_delivery()` - Redirige a `info_page(request, 'shipping')`

### 3. Template (templates/info_page.html)
Un template moderno que:
- Extiende de `base.html` para mantener header y footer
- Carga dinámicamente el título y contenido desde la base de datos
- Usa `{{ page.contenido|safe }}` para renderizar HTML

### 4. Admin de Django (core/admin.py)
Interfaz fácil para editar las páginas:
- Lista todas las páginas disponibles
- Permite editar el título, contenido y meta descripción
- Sección SEO colapsable
- Campos de fecha de creación/modificación (solo lectura)

## Cómo Usar

### Opción 1: A través del Admin Django

1. Inicia sesión en `/admin/`
2. Ve a "Páginas de Información"
3. Selecciona la página que quieres editar (Términos, Privacidad, Devoluciones, Envíos)
4. Edita el contenido en el campo "Contenido"
5. Guarda los cambios

El contenido soporta:
- HTML completo (etiquetas `<h4>`, `<p>`, `<div>`, etc.)
- Estilos CSS
- Emojis
- Enlaces

### Opción 2: A través del Shell de Django

```bash
python manage.py shell

from core.models import InfoPage

# Obtener una página
page = InfoPage.objects.get(slug='terms-conditions')
print(page.contenido)

# Actualizar contenido
page.contenido = "<div class='box'><h4>Nuevo Título</h4><p>Nuevo contenido</p></div>"
page.save()
```

## Características

✅ **Una sola plantilla HTML** (info_page.html) para todas las páginas
✅ **URLs mantenidas** - Las rutas existentes siguen funcionando igual
✅ **Contenido editable desde admin** - No necesitas tocar código
✅ **Historial de cambios** - Las fechas de creación/modificación se registran automáticamente
✅ **SEO optimizado** - Campo para meta descripción
✅ **HTML dinámico** - Puedes usar cualquier etiqueta HTML en el contenido
✅ **Múltiples páginas** - Fácil agregar nuevas páginas si es necesario

## URLs Disponibles

- `/terms-conditions/` → Términos y Condiciones
- `/privacy-policy/` → Política de Privacidad
- `/delivery-return/` → Devoluciones y Cambios
- `/shipping/` → Envíos

## Datos Iniciales Cargados

Se han cargado contenidos base para todas las páginas en español:

### Términos y Condiciones
- Términos y Condiciones Generales
- Cambios en los Términos
- Uso del Sitio Web
- Limitación de Responsabilidad
- Derechos de Autor

### Política de Privacidad
- Privacidad de Datos
- Información que Recopilamos
- Uso de tu Información
- Seguridad de Datos
- Compartir Información
- Contacto

### Devoluciones y Cambios
- Política de Devoluciones
- Plazo de Devolución (14 días)
- Proceso de Devolución
- Cambios (sin costo)
- Artículos en Oferta
- Artículos Defectuosos

### Envíos
- Opciones de Envío
- Envío Estándar (5-7 días)
- Envío Express (2-3 días)
- Envío Gratis (compras > $75)
- Rastreo de Pedido
- Entregas Internacionales
- Entregas No Entregadas

## Cómo Editar el Contenido

1. **En el Admin:**
   - Ve a `Admin Panel > Páginas de Información`
   - Haz clic en la página a editar
   - Modifica el contenido HTML
   - Guarda

2. **Formato HTML recomendado:**
```html
<div class="box">
    <h4>Título de Sección</h4>
    <p>Párrafo descriptivo...</p>
</div>

<div class="box">
    <h4>Otra Sección</h4>
    <p>Más contenido...</p>
    <ul>
        <li>Punto 1</li>
        <li>Punto 2</li>
    </ul>
</div>
```

## Archivos Modificados/Creados

- ✅ `core/models.py` - Modelo `InfoPage` agregado
- ✅ `core/admin.py` - Admin para `InfoPage`
- ✅ `core/views.py` - Vista `info_page()` agregada
- ✅ `templates/info_page.html` - Nuevo template
- ✅ `core/migrations/0008_infopage.py` - Migración de base de datos
- ✅ `setup_info_pages.py` - Script de datos iniciales

## Notas Importantes

1. El contenido se renderiza con `|safe` - esto permite HTML. Solo edita el contenido si confías en la fuente.
2. Las páginas se pueden desactivar sin eliminarlas usando el checkbox "Activo"
3. Si una página está inactiva, mostrará error 404
4. El template mantiene el mismo diseño del sitio (header, footer, menú)

## Próximos Pasos Recomendados

1. Personalizar el contenido HTML con tu branding
2. Agregar logos o imágenes al contenido si es necesario
3. Revisar el SEO de cada página
4. Probar todas las URLs en el navegador
5. Verificar que los enlaces en el footer funcionan correctamente
