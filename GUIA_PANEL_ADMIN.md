# 🎨 Guía Completa - Panel de Administración Ecomus

## 📍 URLs Disponibles

### Panel Admin Personalizado (Ecomus Design):
- **Dashboard**: http://127.0.0.1:8000/admin-panel/productos/dashboard/
- **Lista Productos**: http://127.0.0.1:8000/admin-panel/productos/
- **Agregar Producto**: http://127.0.0.1:8000/admin-panel/productos/agregar/
- **Lista Categorías**: http://127.0.0.1:8000/admin-panel/productos/categorias/
- **Lista Marcas**: http://127.0.0.1:8000/admin-panel/productos/marcas/

### Admin de Django (NO recomendado para tu proyecto):
- http://127.0.0.1:8000/admin/

---

## 🔧 Archivos HTML que Debes Editar

### 📁 Ubicación de archivos HTML originales:
```
selenashop/
  └── admin-ecomus/
      ├── index.html              → Dashboard principal
      ├── product-list.html       → Lista de productos
      ├── add-product.html        → ✅ YA EDITADO
      ├── category-list.html      → Lista de categorías
      ├── new-category.html       → Agregar/editar categoría
      ├── all-user.html           → Lista de usuarios
      ├── add-new-user.html       → Agregar usuario
      └── ... (más archivos)
```

---

## ✏️ Patrón de Edición para TODOS los archivos HTML

### ANTES (HTML estático):
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ecomus - Admin Dashboard</title>
    
    <!-- Theme Style -->
    <link rel="stylesheet" type="text/css" href="css/animate.min.css">
    <link rel="stylesheet" type="text/css" href="css/animation.css">
    <link rel="stylesheet" type="text/css" href="css/bootstrap.css">
    <link rel="stylesheet" type="text/css" href="css/bootstrap-select.min.css">
    <link rel="stylesheet" type="text/css" href="css/styles.css">
    
    <!-- Font -->
    <link rel="stylesheet" href="font/fonts.css">
    
    <!-- Icon -->
    <link rel="stylesheet" href="icon/style.css">
    
    <!-- Favicon -->
    <link rel="shortcut icon" href="images/favicon.png">
    <link rel="apple-touch-icon-precomposed" href="images/favicon.png">
</head>
<body>
    <div class="box-logo">
        <img src="../images/logo/logo.svg" alt="">
    </div>
    <img src="images/products/product-1.jpg" alt="">
    
    <!-- Scripts al final -->
    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/bootstrap-select.min.js"></script>
    <script src="js/apexcharts/apexcharts.js"></script>
    <script src="js/main.js"></script>
</body>
</html>
```

### DESPUÉS (Django template):
```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Selena Store - Panel Admin</title>
    
    <!-- Theme Style -->
    <link rel="stylesheet" type="text/css" href="{% static 'panel_admin/css/animate.min.css' %}">
    <link rel="stylesheet" type="text/css" href="{% static 'panel_admin/css/animation.css' %}">
    <link rel="stylesheet" type="text/css" href="{% static 'panel_admin/css/bootstrap.css' %}">
    <link rel="stylesheet" type="text/css" href="{% static 'panel_admin/css/bootstrap-select.min.css' %}">
    <link rel="stylesheet" type="text/css" href="{% static 'panel_admin/css/styles.css' %}">
    
    <!-- Font -->
    <link rel="stylesheet" href="{% static 'panel_admin/fonts/fonts.css' %}">
    
    <!-- Icon -->
    <link rel="stylesheet" href="{% static 'panel_admin/icon/style.css' %}">
    
    <!-- Favicon -->
    <link rel="shortcut icon" href="{% static 'panel_admin/images/favicon.png' %}">
    <link rel="apple-touch-icon-precomposed" href="{% static 'panel_admin/images/favicon.png' %}">
</head>
<body>
    <div class="box-logo">
        <img src="{% static 'images/logo/logo.svg' %}" alt="">
    </div>
    <img src="{% static 'panel_admin/images/products/product-1.jpg' %}" alt="">
    
    <!-- Scripts al final -->
    <script src="{% static 'panel_admin/js/jquery.min.js' %}"></script>
    <script src="{% static 'panel_admin/js/bootstrap.min.js' %}"></script>
    <script src="{% static 'panel_admin/js/bootstrap-select.min.js' %}"></script>
    <script src="{% static 'panel_admin/js/apexcharts/apexcharts.js' %}"></script>
    <script src="{% static 'panel_admin/js/main.js' %}"></script>
</body>
</html>
```

---

## 🔍 Buscar y Reemplazar - Uso de Editor de Texto

### Usando Visual Studio Code (Recomendado):

1. **Abrir el archivo HTML** (ejemplo: `admin-ecomus/product-list.html`)

2. **Buscar y Reemplazar** (Ctrl+H):

#### PASO 1: Agregar {% load static %} al inicio
- Buscar: `<!DOCTYPE html>`
- Reemplazar con:
```html
{% load static %}
<!DOCTYPE html>
```

#### PASO 2: Reemplazar CSS
- Buscar: `href="css/`
- Reemplazar con: `href="{% static 'panel_admin/css/`

- Buscar: `href="font/`
- Reemplazar con: `href="{% static 'panel_admin/fonts/`

- Buscar: `href="icon/`
- Reemplazar con: `href="{% static 'panel_admin/icon/`

#### PASO 3: Reemplazar imágenes
- Buscar: `src="images/`
- Reemplazar con: `src="{% static 'panel_admin/images/`

- Buscar: `src="../images/`
- Reemplazar con: `src="{% static 'images/`

#### PASO 4: Reemplazar JavaScript
- Buscar: `src="js/`
- Reemplazar con: `src="{% static 'panel_admin/js/`

#### PASO 5: Cerrar etiquetas static
- Buscar: `.css">`
- Reemplazar con: `.css' %}">`

- Buscar: `.js">`
- Reemplazar con: `.js' %}">`

- Buscar: `.png">`
- Reemplazar con: `.png' %}">`

- Buscar: `.jpg"`
- Reemplazar con: `.jpg' %}"`

- Buscar: `.svg"`
- Reemplazar con: `.svg' %}"`

---

## 📝 Archivos Prioritarios a Editar

### 1. Dashboard Principal (index.html)
```bash
# Copiar y mover
cp admin-ecomus/index.html templates/admin/dashboard.html
```

Luego editar `templates/admin/dashboard.html` con los reemplazos de arriba.

### 2. Lista de Productos (product-list.html)
```bash
cp admin-ecomus/product-list.html templates/admin/productos/producto_lista.html
```

### 3. Agregar Producto (add-product.html)
✅ **YA LO TIENES EDITADO** - Solo necesitas moverlo:
```bash
# Ya está en admin-ecomus/add-product.html con las rutas actualizadas
# Crear la vista y template correspondiente
```

### 4. Lista de Categorías (category-list.html)
```bash
cp admin-ecomus/category-list.html templates/admin/productos/categoria_lista.html
```

### 5. Nueva Categoría (new-category.html)
```bash
cp admin-ecomus/new-category.html templates/admin/productos/categoria_form.html
```

---

## 🚀 Cómo Probar el Panel

### 1. Iniciar el servidor:
```bash
python manage.py runserver
```

### 2. Acceder a las URLs:
- Dashboard: http://127.0.0.1:8000/admin-panel/productos/dashboard/
- Productos: http://127.0.0.1:8000/admin-panel/productos/
- Categorías: http://127.0.0.1:8000/admin-panel/productos/categorias/

---

## ⚠️ Problemas Comunes y Soluciones

### Problema 1: "TemplateDoesNotExist"
**Causa**: No creaste el archivo template en la ubicación correcta

**Solución**:
```bash
# Verificar que existe:
templates/admin/dashboard.html
templates/admin/productos/producto_lista.html
templates/admin/productos/categoria_lista.html
```

### Problema 2: Los estilos CSS no cargan
**Causa**: Las rutas estáticas no están correctamente configuradas

**Solución**:
1. Verificar que agregaste `{% load static %}` al inicio del HTML
2. Verificar que las rutas son `{% static 'panel_admin/css/...' %}`
3. Ejecutar: `python manage.py collectstatic` (si es necesario)

### Problema 3: Las imágenes no aparecen
**Causa**: Rutas incorrectas o archivos no en `static/panel_admin/images/`

**Solución**:
```python
# En settings.py debe estar:
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'admin-ecomus',
]
```

---

## 📊 Estructura Final de Carpetas

```
selenashop/
├── apps/
│   └── productos/
│       ├── views.py          → Todas las vistas (dashboard, productos, categorías)
│       └── urls.py           → URLs del panel admin
├── static/
│   └── panel_admin/          → ✅ Archivos estáticos organizados
│       ├── css/
│       ├── js/
│       ├── images/
│       ├── fonts/
│       └── icon/
├── templates/
│   └── admin/                → Templates del panel personalizado
│       ├── dashboard.html          → Dashboard principal
│       └── productos/
│           ├── producto_lista.html
│           ├── producto_form.html
│           ├── categoria_lista.html
│           └── categoria_form.html
├── admin-ecomus/             → Archivos HTML originales (para referencia)
│   ├── index.html
│   ├── product-list.html
│   ├── add-product.html      → ✅ Ya editado
│   └── ...
└── manage.py
```

---

## 🎯 Próximos Pasos

1. **Editar `admin-ecomus/index.html`** (Dashboard principal)
2. **Editar `admin-ecomus/product-list.html`** (Lista de productos)
3. **Editar `admin-ecomus/category-list.html`** (Lista de categorías)
4. **Mover archivos editados** a `templates/admin/`
5. **Probar cada página** accediendo a las URLs

---

## 💡 Tip Final

Puedes usar un comando de PowerShell para hacer reemplazos masivos:

```powershell
# Ejemplo: reemplazar en todos los HTML de admin-ecomus
Get-ChildItem -Path admin-ecomus -Filter *.html | ForEach-Object {
    (Get-Content $_.FullName) `
        -replace 'href="css/', 'href="{% static ''panel_admin/css/' `
        -replace 'src="js/', 'src="{% static ''panel_admin/js/' `
        | Set-Content $_.FullName
}
```

**PERO** es más seguro hacerlo archivo por archivo manualmente para evitar errores.

---

¿Necesitas ayuda editando algún archivo específico? ¡Dime cuál y te ayudo! 🚀
