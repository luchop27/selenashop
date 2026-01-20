# 📍 Sistema de Recuperación de Contraseña - Ubicaciones Frontend

## ✅ Templates Actualizados

### 1. **login.html** - Página Principal de Login
**Ubicación:** `templates/login.html`

**Características:**
- ✅ Sección #recover con formulario de recuperación
- ✅ Sección #login con formulario de inicio de sesión
- ✅ Link "Forgot your password?" que cambia entre secciones
- ✅ Formulario POST a `{% url 'usuarios:password_reset_request' %}`
- ✅ Campo email con validación
- ✅ Botón "Enviar código"

**Código clave:**
```html
<div id="recover">
    <h5 class="mb_24">Restablecer contraseña</h5>
    <p class="mb_30">Te enviaremos un código de 6 dígitos a tu correo electrónico</p>
    <form action="{% url 'usuarios:password_reset_request' %}" method="post">
        {% csrf_token %}
        <!-- Campo email -->
        <button type="submit">Enviar código</button>
    </form>
</div>
```

---

### 2. **base.html** - Modal Global
**Ubicación:** `templates/base.html`

**Modal de Login (línea ~610):**
- ✅ Modal #login con formulario de inicio de sesión
- ✅ Link "¿Olvidaste tu contraseña?" que abre #forgotPassword

**Modal de Recuperación (línea ~652):**
- ✅ Modal #forgotPassword con formulario de recuperación
- ✅ Formulario POST a `{% url 'usuarios:password_reset_request' %}`
- ✅ JavaScript para deshabilitar botón durante envío
- ✅ Campo email con ID único: `modal-reset-email`
- ✅ Botón "Enviar código" con ID: `modal-reset-submit`

**JavaScript incluido:**
```javascript
const modalResetForm = document.getElementById('modal-reset-form');
modalResetForm.addEventListener('submit', function(e) {
    // Deshabilitar botón durante envío
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Enviando...</span>';
});
```

**Accesible desde:**
- Icono de usuario en header (navbar)
- Link en footer "Iniciar Sesión"
- Cualquier página del sitio

---

### 3. **wishlist.html** - Modal en Wishlist
**Ubicación:** `templates/wishlist.html` (línea ~2881)

**Características:**
- ✅ Modal #forgotPassword actualizado
- ✅ Formulario POST a `{% url 'usuarios:password_reset_request' %}`
- ✅ JavaScript para manejar envío
- ✅ Campo email con ID único: `wishlist-reset-email`
- ✅ Botón con ID: `wishlist-reset-submit`

**JavaScript incluido:**
```javascript
const wishlistResetForm = document.getElementById('wishlist-reset-form');
wishlistResetForm.addEventListener('submit', function(e) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Enviando...</span>';
});
```

---

### 4. **password_reset_verify.html** - Verificación de Código
**Ubicación:** `templates/password_reset_verify.html`

**Características:**
- ✅ 6 campos individuales para código numérico
- ✅ Auto-focus y auto-avance entre campos
- ✅ Soporte para pegar código completo (Ctrl+V)
- ✅ Timer en tiempo real (cuenta regresiva de 15 minutos)
- ✅ Botón "Reenviar código" con cooldown de 60 segundos
- ✅ Validación solo números (0-9)
- ✅ Formulario POST a `{% url 'usuarios:password_reset_verify' %}`

**JavaScript incluido:**
```javascript
// Auto-avance entre campos
// Manejo de pegado (paste)
// Timer de expiración
// AJAX para reenvío de código
```

---

### 5. **password_reset_complete.html** - Nueva Contraseña
**Ubicación:** `templates/password_reset_complete.html`

**Características:**
- ✅ Formulario de nueva contraseña
- ✅ Indicador de fortaleza de contraseña (débil/media/fuerte)
- ✅ Checklist de requisitos visible
- ✅ Validación de coincidencia de contraseñas
- ✅ Validación en tiempo real
- ✅ Formulario POST a `{% url 'usuarios:password_reset_complete' %}`

**JavaScript incluido:**
```javascript
// Validación de fortaleza
// Checklist de requisitos
// Validación de coincidencia
```

---

## 🔗 Flujo Completo del Usuario

### Desde Login.html:
1. Usuario va a `/usuarios/login/`
2. Hace clic en "Forgot your password?"
3. Sección cambia a #recover
4. Ingresa email y envía
5. Redirige a `/usuarios/password-reset/verify/`
6. Ingresa código de 6 dígitos
7. Redirige a `/usuarios/password-reset/complete/`
8. Ingresa nueva contraseña
9. Redirige a `/usuarios/login/` con mensaje de éxito

### Desde Modal (Base.html):
1. Usuario hace clic en icono de login
2. Modal #login se abre
3. Hace clic en "¿Olvidaste tu contraseña?"
4. Modal #forgotPassword se abre
5. Ingresa email y envía
6. **Página completa redirige** a `/usuarios/password-reset/verify/`
7. Resto del flujo igual (pasos 6-9 arriba)

### Desde Wishlist:
1. Usuario está en wishlist
2. Intenta login en modal
3. Hace clic en "Forgot your password?"
4. Modal #forgotPassword se abre
5. Resto del flujo igual

---

## 📝 URLs Configuradas

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/usuarios/password-reset/` | `password_reset_request_code` | Solicitar código (POST) |
| `/usuarios/password-reset/verify/` | `password_reset_verify` | Ingresar código de 6 dígitos |
| `/usuarios/password-reset/complete/` | `password_reset_complete` | Establecer nueva contraseña |
| `/usuarios/password-reset/resend/` | `password_reset_resend` | Reenviar código (AJAX) |

---

## 🎨 Consistencia de Diseño

### Todos los formularios usan:
- ✅ Clase `.tf-login-form`
- ✅ Clase `.tf-field style-1` para campos
- ✅ Clase `.tf-field-input tf-input` para inputs
- ✅ Clase `.tf-field-label` para labels
- ✅ Clase `.tf-btn btn-fill` para botones primarios
- ✅ Clase `.btn-link link` para links secundarios

### Mensajes de feedback:
- ✅ Success: clase `alert-success`
- ✅ Error: clase `alert-error` o `alert-danger`
- ✅ Django messages system integrado

---

## 🔒 Seguridad Implementada

### Frontend:
1. **CSRF Token** en todos los formularios
2. **Validación HTML5** (email, required)
3. **Deshabilitación de botón** durante envío (previene doble submit)
4. **IDs únicos** para evitar conflictos entre modales

### Backend:
1. **Códigos de un solo uso** (se marcan como usados)
2. **Expiración de 15 minutos**
3. **Cooldown de 60 segundos** para reenvío
4. **Validación de sesión** (email guardado en sesión)
5. **Mensajes genéricos** si email no existe (previene enumeración)

---

## 📱 Responsive

Todos los formularios son responsive y funcionan en:
- ✅ Desktop (>992px)
- ✅ Tablet (768px-992px)
- ✅ Mobile (<768px)

Los modales usan clase `.modalCentered` que centra en todos los dispositivos.

---

## 🧪 Cómo Probar Cada Ubicación

### 1. Login.html:
```
http://127.0.0.1:8000/usuarios/login/
→ Scroll a "Restablecer contraseña"
→ Ingresar email
→ Enviar
```

### 2. Modal Base:
```
http://127.0.0.1:8000/
→ Clic en icono de usuario (header)
→ Clic en "¿Olvidaste tu contraseña?"
→ Ingresar email
→ Enviar
```

### 3. Modal Wishlist:
```
http://127.0.0.1:8000/wishlist/
→ Intentar login
→ Clic en "Forgot your password?"
→ Ingresar email
→ Enviar
```

### 4. Verificación:
```
Se redirige automáticamente después del paso anterior
http://127.0.0.1:8000/usuarios/password-reset/verify/
→ Ingresar código de 6 dígitos
→ Enviar
```

### 5. Nueva Contraseña:
```
Se redirige automáticamente después del paso anterior
http://127.0.0.1:8000/usuarios/password-reset/complete/
→ Ingresar nueva contraseña
→ Confirmar contraseña
→ Enviar
```

---

## ✨ Características Especiales

### Auto-avance en Código:
- Al escribir un dígito, el cursor salta al siguiente campo
- Al pegar (Ctrl+V), el código se distribuye automáticamente

### Timer en Tiempo Real:
- Muestra cuenta regresiva: "14:32 restantes"
- Cuando expira, muestra "Código expirado"
- Botón de reenvío se activa

### Indicador de Fortaleza:
- Débil (rojo): < 6 caracteres
- Media (amarillo): 6-8 caracteres con letras
- Fuerte (verde): >8 caracteres con letras + números

### Validación Visual:
- ✅ Verde cuando cumple requisito
- ⭕ Gris cuando no cumple
- Actualización en tiempo real

---

## 🆘 Troubleshooting

### Modal no se abre:
**Verificar:** Bootstrap JS está cargado
```html
<script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
```

### Formulario no envía:
**Verificar:** 
1. CSRF token presente: `{% csrf_token %}`
2. Método POST: `method="post"`
3. Action correcto: `action="{% url 'usuarios:password_reset_request' %}"`

### No redirige después de enviar:
**Verificar:**
1. Vista retorna `redirect('usuarios:password_reset_verify')`
2. Email guardado en sesión
3. No hay errores en logs del servidor

### Timer no funciona:
**Verificar:**
1. JavaScript de password_reset_verify.html está cargado
2. Atributo `data-tiempo="{{ tiempo_restante }}"` está presente
3. Console del navegador para errores JS

---

## 📦 Archivos Relacionados

### Templates:
- `templates/login.html`
- `templates/base.html`
- `templates/wishlist.html`
- `templates/password_reset_verify.html`
- `templates/password_reset_complete.html`

### Backend:
- `apps/usuarios/views_password_reset.py`
- `apps/usuarios/urls.py`
- `apps/usuarios/models.py` (PasswordResetCode)

### Email:
- `core/email_backend.py` (Backend robusto)
- `selenashop/settings.py` (Configuración email)

---

## ✅ Checklist de Implementación

- [x] login.html con formulario de recuperación
- [x] base.html modal #login con link a recuperación
- [x] base.html modal #forgotPassword funcional
- [x] wishlist.html modal actualizado
- [x] password_reset_verify.html con 6 campos
- [x] password_reset_complete.html con validación
- [x] URLs configuradas en usuarios/urls.py
- [x] Vistas con logging completo
- [x] Backend de email robusto
- [x] JavaScript para UX mejorada
- [x] Diseño consistente en todos los templates
- [x] Responsive en todos los dispositivos
- [x] Seguridad implementada (CSRF, validaciones)
- [x] Mensajes de error/éxito
- [x] Documentación completa

---

## 🚀 Listo para Producción

El sistema está implementado en **todas las ubicaciones** del frontend donde un usuario puede iniciar sesión:

1. ✅ Página de login standalone
2. ✅ Modal de login en navbar
3. ✅ Modal de login en footer
4. ✅ Modal de login en wishlist
5. ✅ Cualquier otra página que use base.html

**Todos apuntan al mismo flujo backend** - un sistema unificado y consistente.
