# 🏗️ Diagrama de Arquitectura - Sistema de Páginas de Ayuda

## Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO FINAL                            │
│                                                                  │
│  Visita: /términos-condiciones/ (o cualquier otra página)      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    URLS (core/urls.py)                          │
│                                                                  │
│  path('términos-condiciones/', views.terms_conditions, ...)    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VISTAS (core/views.py)                         │
│                                                                  │
│  def terms_conditions(request):                                 │
│    pagina = PaginaAyuda.objects.get(tipo='terminos')           │
│    return render(..., {'pagina': pagina})                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BASE DE DATOS (BD)                              │
│                                                                  │
│  Tabla: ayudas_paginaayuda                                     │
│  ┌────────────────────────────────────────────────────┐         │
│  │ id │ tipo │ titulo │ contenido │ activo │ fechas  │         │
│  ├────────────────────────────────────────────────────┤         │
│  │ 1  │ term │ Térm.. │ <html>... │  ✓    │ 2026... │         │
│  │ 2  │ priv │ Políc..│ <html>... │  ✓    │ 2026... │         │
│  │ 3  │ devl │ Devol..│ <html>... │  ✓    │ 2026... │         │
│  │ 4  │ envs │ Envíos │ <html>... │  ✓    │ 2026... │         │
│  └────────────────────────────────────────────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TEMPLATE (terms-conditions.html)              │
│                                                                  │
│  {{ pagina.titulo }}                                            │
│  {{ pagina.contenido|safe }}                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HTML RENDERIZADO                             │
│                      (Al Usuario)                               │
│                                                                  │
│  Título: "Términos y Condiciones"                              │
│  Contenido: HTML personalizado con estilos                      │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo del Admin

```
┌─────────────────────────────────────────────────────────────────┐
│                      ADMINISTRADOR                              │
│                    Va a /admin/                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            ADMIN: Páginas de Ayuda (admin.py)                   │
│                                                                  │
│  @admin.register(PaginaAyuda)                                   │
│  class PaginaAyudaAdmin(admin.ModelAdmin):                      │
│    - list_display: Tipo, Título, Activo, Fecha                │
│    - fieldsets: Información, Contenido, Fechas                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                  ┌────────┴───────────┐
                  │                    │
                  ▼                    ▼
        ┌──────────────┐      ┌──────────────┐
        │   EDITA      │      │    GUARDA    │
        │  CONTENIDO   │      │  CAMBIOS     │
        └──────────────┘      └──────┬───────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  BASE DE DATOS   │
                          │  (actualizada)   │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  USUARIO FINAL   │
                          │  ve los cambios  │
                          │  INMEDIATAMENTE  │
                          └──────────────────┘
```

## Estructura de Carpetas

```
selenashop/
│
├── apps/
│   └── ayudas/                    ← NUEVA APP
│       ├── migrations/
│       │   ├── __init__.py
│       │   └── 0001_initial.py    ← TABLA CREADA
│       ├── __init__.py
│       ├── admin.py               ← ADMIN PANEL
│       ├── apps.py                ← CONFIG
│       ├── models.py              ← MODELO
│       ├── tests.py
│       ├── urls.py                ← URLS
│       └── views.py               ← VISTAS
│
├── core/
│   ├── views.py                   ← ACTUALIZADO (4 funciones)
│   └── urls.py                    ← ACTUALIZADO
│
├── selenashop/
│   ├── settings.py                ← ACTUALIZADO (INSTALLED_APPS)
│   └── urls.py                    ← ACTUALIZADO (includes)
│
├── templates/
│   └── terms-conditions.html       ← ACTUALIZADO (dinámico)
│
├── PRIMEROS_PASOS_PAGINAS_AYUDA.md          ← NUEVO
├── GUIA_PAGINAS_AYUDA_DINAMICAS.md          ← NUEVO
├── DOCUMENTACION_TECNICA_PAGINAS_AYUDA.md   ← NUEVO
├── RESUMEN_IMPLEMENTACION_PAGINAS_AYUDA.md  ← NUEVO
├── init_paginas_ayuda.py                    ← NUEVO (ejecutado)
│
└── manage.py
```

## Relaciones y Dependencias

```
┌──────────────────────────────────────────┐
│      DJANGO FRAMEWORK (5.2.7)            │
├──────────────────────────────────────────┤
│  ├─ ORM (Base de Datos)                  │
│  ├─ Admin Interface                      │
│  ├─ URL Router                           │
│  ├─ Template Engine                      │
│  └─ Security (CSRF, XSS)                 │
└──────────────────────┬───────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌─────────┐    ┌──────────┐
   │ Models │    │  Views  │    │Templates │
   └────┬───┘    └────┬────┘    └────┬─────┘
        │             │              │
        │        ┌────┴───────┐      │
        │        │            │      │
        ▼        ▼            ▼      ▼
   ┌─────────────────────────────────────┐
   │     SISTEMA DE PÁGINAS DE AYUDA    │
   │                                     │
   │  PaginaAyuda (Model)               │
   │  ├─ tipo                            │
   │  ├─ titulo                          │
   │  ├─ contenido                       │
   │  └─ activo                          │
   │                                     │
   │  PaginaAyudaAdmin (Admin)          │
   │  ├─ list_display                    │
   │  ├─ fieldsets                       │
   │  └─ search_fields                   │
   │                                     │
   │  Views                              │
   │  ├─ terms_conditions()              │
   │  ├─ privacy_policy()                │
   │  ├─ delivery_return()               │
   │  └─ shipping_delivery()             │
   └─────────────────────────────────────┘
```

## Flujo de Datos (Detallado)

```
1. USUARIO ACCEDE A /TÉRMINOS-CONDICIONES/
   │
   ├─ URL dispatcher busca coincidencia
   └─ Encuentra: path('términos-condiciones/', views.terms_conditions)

2. SE EJECUTA: core.views.terms_conditions(request)
   │
   ├─ Importa: from apps.ayudas.models import PaginaAyuda
   ├─ Query: PaginaAyuda.objects.get(tipo='terminos', activo=True)
   │  │
   │  └─ SQL generado:
   │     SELECT * FROM ayudas_paginaayuda 
   │     WHERE tipo='terminos' AND activo=1
   │
   └─ Retorna render(..., {'pagina': pagina})

3. TEMPLATE: templates/terms-conditions.html
   │
   ├─ {% extends "base.html" %}
   ├─ {{ pagina.titulo }}
   │  └─ Inserta: "Términos y Condiciones"
   │
   └─ {{ pagina.contenido|safe }}
      └─ Renderiza HTML personalizado

4. HTML FINAL
   │
   ├─ Base template (header, footer, nav)
   ├─ Título dinámico
   ├─ Contenido HTML personal
   └─ Se envía al navegador del usuario
```

## Tabla de Base de Datos

```
ayudas_paginaayuda
┌────┬───────────┬──────────────────────┬─────────────────┬────────┬─────────────────────┐
│ ID │   TIPO    │       TITULO         │    CONTENIDO    │ ACTIVO │ FECHA_MODIFICACION  │
├────┼───────────┼──────────────────────┼─────────────────┼────────┼─────────────────────┤
│ 1  │ terminos  │ Términos y Cond...   │ <div><h4>...</h4><p>...</p></div>   │   ✓    │ 2026-01-26 12:30  │
│ 2  │ privacidad│ Política de Priv...  │ <div><h4>...</h4><p>...</p></div>   │   ✓    │ 2026-01-26 12:30  │
│ 3  │ devoluciones│ Devoluciones...    │ <div><h4>...</h4><p>...</p></div>   │   ✓    │ 2026-01-26 12:30  │
│ 4  │ envios    │ Envíos y Entregas    │ <div><h4>...</h4><p>...</p></div>   │   ✓    │ 2026-01-26 12:30  │
└────┴───────────┴──────────────────────┴─────────────────┴────────┴─────────────────────┘
```

## URLs Mapeadas

```
USUARIO FINAL (Frontend)
├─ /términos-condiciones/          → core.views.terms_conditions()
├─ /politica-privacidad/           → core.views.privacy_policy()
├─ /devoluciones-cambios/          → core.views.delivery_return()
└─ /envios/                        → core.views.shipping_delivery()

URLS OPCIONALES (apps/ayudas/urls.py)
├─ /ayuda/términos-condiciones/    → ayudas.views.terms_conditions()
├─ /ayuda/politica-privacidad/     → ayudas.views.privacy_policy()
├─ /ayuda/devoluciones-cambios/    → ayudas.views.delivery_return()
└─ /ayuda/envios/                  → ayudas.views.shipping()

ADMIN
└─ /admin/ayudas/paginaayuda/      → Admin Panel
```

## Tecnologías Utilizadas

```
┌──────────────────────────────────────┐
│  BACKEND                             │
├──────────────────────────────────────┤
│  ✓ Django 5.2.7                      │
│  ✓ Python 3.x                        │
│  ✓ Base de Datos (SQLite/MySQL)      │
│  ✓ ORM Django                        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  FRONTEND                            │
├──────────────────────────────────────┤
│  ✓ HTML5                             │
│  ✓ Django Templates                  │
│  ✓ Bootstrap (desde base.html)       │
│  ✓ CSS existente                     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  ADMIN                               │
├──────────────────────────────────────┤
│  ✓ Django Admin                      │
│  ✓ Interfaz web nativa               │
│  ✓ Búsqueda y filtros                │
│  ✓ Validación de datos               │
└──────────────────────────────────────┘
```

## Resumen de Flujos

| Acción | Flujo | Tiempo |
|--------|-------|--------|
| Editar contenido | Admin → BD | < 1 segundo |
| Ver cambios | Actualizar página | < 1 segundo |
| Agregar página | Código → Migración | ~ 1 minuto |
| Query a BD | SELECT simple | < 100ms |

---

**Arquitectura limpia, modular y escalable** ✅
