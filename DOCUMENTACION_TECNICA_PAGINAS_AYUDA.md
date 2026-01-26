# 🔧 Documentación Técnica - Sistema de Páginas de Ayuda

## Estructura del Proyecto

```
apps/
└── ayudas/
    ├── migrations/
    │   └── 0001_initial.py
    ├── __init__.py
    ├── admin.py          # Configuración del admin
    ├── apps.py           # Configuración de la app
    ├── models.py         # Modelo PaginaAyuda
    ├── tests.py
    ├── urls.py           # URLs de la app
    └── views.py          # Vistas para servir páginas
```

## Modelo de Datos: PaginaAyuda

```python
class PaginaAyuda(models.Model):
    tipo = CharField(choices=[
        ('terminos', 'Términos y Condiciones'),
        ('privacidad', 'Política de Privacidad'),
        ('devoluciones', 'Devoluciones y Cambios'),
        ('envios', 'Envíos'),
    ])
    titulo = CharField(max_length=200)
    contenido = TextField()  # Permite HTML
    activo = BooleanField(default=True)
    fecha_creacion = DateTimeField(auto_now_add=True)
    fecha_modificacion = DateTimeField(auto_now=True)
```

## URLs

### URLs de la App (`apps/ayudas/urls.py`)
```
/ayuda/términos-condiciones/    → views.terms_conditions
/ayuda/devoluciones-cambios/    → views.delivery_return
/ayuda/envios/                  → views.shipping
/ayuda/politica-privacidad/     → views.privacy_policy
```

### URLs del Core (`core/urls.py`)
```
/términos-condiciones/          → core.views.terms_conditions (actualizado)
/privacy-policy/                → core.views.privacy_policy (actualizado)
/delivery-return/               → core.views.delivery_return (actualizado)
/shipping/                      → core.views.shipping_delivery (actualizado)
```

## Vistas

### core/views.py
Las vistas han sido actualizadas para obtener datos dinámicamente:

```python
def terms_conditions(request):
    """Renderiza la página de términos desde el admin"""
    from apps.ayudas.models import PaginaAyuda
    pagina = None
    try:
        pagina = PaginaAyuda.objects.get(tipo='terminos', activo=True)
    except PaginaAyuda.DoesNotExist:
        pass
    
    return render(request, 'terms-conditions.html', {'pagina': pagina})
```

## Template

### templates/terms-conditions.html
```django
{% extends "base.html" %}

{% block content %}
<div class="tf-page-title style-2">
    <div class="container-full">
        <div class="heading text-center">{{ pagina.titulo }}</div>
    </div>
</div>

<section class="flat-spacing-25">
    <div class="container">
        <div class="tf-main-area-page tf-terms-conditions">
            {% if pagina and pagina.contenido %}
                {{ pagina.contenido|safe }}  <!-- Renderiza HTML -->
            {% else %}
                <div class="box">
                    <p class="text-center text-muted">No hay contenido disponible</p>
                </div>
            {% endif %}
        </div>
    </div>
</section>
{% endblock %}
```

## Configuración Django

### settings.py
```python
INSTALLED_APPS = [
    ...
    'apps.ayudas',  # Agregada
    'core',
]
```

### urls.py
```python
urlpatterns = [
    ...
    path('ayuda/', include('apps.ayudas.urls')),  # Agregada
    ...
]
```

## Admin

### admin.py
```python
@admin.register(PaginaAyuda)
class PaginaAyudaAdmin(admin.ModelAdmin):
    list_display = ('get_tipo_display', 'titulo', 'activo', 'fecha_modificacion')
    list_filter = ('tipo', 'activo')
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('tipo', 'titulo', 'activo')
        }),
        ('Contenido', {
            'fields': ('contenido',),
            'classes': ('wide',),
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
```

## Flujo de Datos

```
Usuario accede a /términos-condiciones/
        ↓
core.views.terms_conditions(request)
        ↓
Busca en BD: PaginaAyuda.objects.get(tipo='terminos', activo=True)
        ↓
Renderiza: templates/terms-conditions.html con contexto {'pagina': pagina}
        ↓
Template muestra: pagina.titulo y pagina.contenido|safe
        ↓
Usuario ve la página con contenido personalizado
```

## Migraciones Realizadas

```bash
# Crear migraciones
python manage.py makemigrations ayudas
# Resultado: apps/ayudas/migrations/0001_initial.py

# Aplicar migraciones
python manage.py migrate ayudas
# Resultado: Tabla 'ayudas_paginaayuda' creada en la BD
```

## Inicialización de Datos

Se ejecutó el script `init_paginas_ayuda.py` que:
1. Crea 4 registros en la tabla PaginaAyuda
2. Cada uno con contenido de ejemplo
3. Todos marcados como activos

```python
# Ejecutado con:
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings'); 
import django; django.setup(); exec(open('init_paginas_ayuda.py').read())"
```

## Casos de Uso Avanzados

### 1. Agregar una Nueva Página de Ayuda

Editar `apps/ayudas/models.py`:
```python
TIPOS_AYUDA = [
    ('terminos', 'Términos y Condiciones'),
    ('devoluciones', 'Devoluciones y Cambios'),
    ('envios', 'Envíos'),
    ('privacidad', 'Política de Privacidad'),
    ('faq', 'Preguntas Frecuentes'),  # NUEVA
]
```

Editar `apps/ayudas/urls.py`:
```python
path('faq/', views.faq_page, name='faq-help'),
```

Agregar vista en `apps/ayudas/views.py`:
```python
def faq_page(request):
    pagina = get_object_or_404(PaginaAyuda, tipo='faq', activo=True)
    return render(request, 'terms-conditions.html', {'pagina': pagina})
```

Ejecutar migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Cambiar el Template

Si quieres un template diferente para una página específica:
```python
def privacy_policy(request):
    pagina = get_object_or_404(PaginaAyuda, tipo='privacidad', activo=True)
    # Usar template diferente
    return render(request, 'privacy-custom.html', {'pagina': pagina})
```

### 3. Agregar Validación de Contenido

```python
class PaginaAyuda(models.Model):
    ...
    def clean(self):
        if len(self.contenido) < 50:
            raise ValidationError('El contenido debe tener al menos 50 caracteres')
```

## Queries SQL Generadas

```sql
-- Obtener página activa de términos
SELECT * FROM ayudas_paginaayuda 
WHERE tipo='terminos' AND activo=1

-- Listar todas las páginas
SELECT * FROM ayudas_paginaayuda 
ORDER BY tipo

-- Actualizar contenido
UPDATE ayudas_paginaayuda 
SET contenido='...', fecha_modificacion=NOW() 
WHERE id=1
```

## Performance

- **Índices**: El campo `tipo` tiene `unique=True` → índice automático
- **Caché**: Se puede agregar caché de vistas Django si hay mucho tráfico
- **Queries**: Solo 1 query por página (O(1))

## Troubleshooting

### Error: "no such table: ayudas_paginaayuda"
```bash
python manage.py migrate
```

### Error: "PaginaAyuda matching query does not exist"
- Verifica que el registro existe en la BD
- Comprueba que `activo=True`
- Verifica que el `tipo` es correcto

### HTML no se renderiza
- Verifica que usas `{{ contenido|safe }}` en el template
- No uses `{{ contenido|escape }}`

## Conclusión

Este sistema es:
- ✅ **Modular**: Fácil de mantener y extender
- ✅ **Seguro**: Solo admin puede editar
- ✅ **Flexible**: HTML personalizado
- ✅ **Escalable**: Agregar más páginas es trivial
