# 📧 Guía de Configuración de Email para Producción

## 🎯 Por Qué NO Usar Gmail en Producción

Gmail está diseñado para uso personal, no para aplicaciones:
- ❌ Límite de 500 emails por día
- ❌ Problemas de certificados SSL con Python 3.11+
- ❌ Puede bloquear tu cuenta por "actividad sospechosa"
- ❌ No es profesional (emails van desde @gmail.com)
- ❌ No tiene tracking ni analytics

## ✅ Servicios Profesionales Recomendados

### 1️⃣ SendGrid (⭐ RECOMENDADO)

**Plan Gratis:** 100 emails/día PERMANENTE

**Ventajas:**
- ✅ Fácil configuración
- ✅ Dashboard con estadísticas
- ✅ Verificación de email incluida
- ✅ Excelente deliverability
- ✅ API REST además de SMTP

**Configuración:**

1. **Crear cuenta:** https://sendgrid.com/

2. **Crear API Key:**
   - Settings → API Keys → Create API Key
   - Permisos: Full Access
   - Copia la key (solo se muestra una vez)

3. **Verificar dominio (opcional):**
   - Settings → Sender Authentication
   - Verificar tu dominio para mejor deliverability

4. **Configurar en Django:**
```python
# En producción (.env)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=Selena Shop <noreply@tudominio.com>
```

---

### 2️⃣ Mailgun

**Plan Gratis:** 5,000 emails/mes por 3 meses

**Ventajas:**
- ✅ API simple
- ✅ Buenos logs
- ✅ Validación de emails
- ✅ Tracking de clicks/aperturas

**Configuración:**

1. **Crear cuenta:** https://www.mailgun.com/

2. **Obtener credenciales:**
   - Sending → Domain Settings → SMTP Credentials

3. **Configurar en Django:**
```python
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@tu-sandbox.mailgun.org
EMAIL_HOST_PASSWORD=tu_password_smtp
```

---

### 3️⃣ Amazon SES

**Plan Gratis:** 62,000 emails/mes desde EC2/Lambda

**Ventajas:**
- ✅ Muy barato después del free tier
- ✅ Escalable infinitamente
- ✅ Integración con AWS

**Desventajas:**
- ⚠️ Configuración más compleja
- ⚠️ Sale de sandbox requiere solicitud

**Configuración:**

1. **Verificar email en AWS SES**

2. **Crear credenciales SMTP:**
   - SES → SMTP Settings → Create SMTP Credentials

3. **Configurar en Django:**
```python
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_HOST_USER=AKIAIOSFODNN7EXAMPLE
EMAIL_HOST_PASSWORD=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## 🔧 Configuración en tu Proyecto

### Paso 1: Instalar python-decouple (para variables de entorno)

```bash
pip install python-decouple
```

### Paso 2: Modificar settings.py

Ya está configurado en tu proyecto. Solo necesitas:

1. **Crear archivo `.env` en la raíz del proyecto:**
```bash
cp .env.example .env
```

2. **Editar `.env` con tus credenciales de SendGrid:**
```env
PRODUCTION=True
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu_api_key_aqui
DEFAULT_FROM_EMAIL=Selena Shop <noreply@tudominio.com>
```

3. **Asegurarte que `.env` esté en `.gitignore`** (para no subir credenciales)

---

## 🧪 Cómo Probar en Desarrollo

### Opción 1: Backend de Consola (Actual)

Los emails se muestran en la terminal donde corre el servidor.

**Ventajas:**
- ✅ No necesita configuración
- ✅ Ves el contenido completo del email
- ✅ No gasta cuota de ningún servicio

**Uso:**
```python
# En settings.py (ya configurado para desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Opción 2: Mailtrap (para ver emails con diseño)

Servicio que captura emails en desarrollo.

1. **Crear cuenta:** https://mailtrap.io/ (gratis)

2. **Configurar en development:**
```python
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'tu_username'
EMAIL_HOST_PASSWORD = 'tu_password'
```

---

## 📊 Monitoreo y Analytics

### SendGrid Dashboard

- Emails enviados/entregados/rebotados
- Tasa de apertura (si activas tracking)
- Tasa de clicks
- Lista de emails bloqueados

### Webhooks para tracking avanzado

Puedes configurar webhooks para recibir eventos:
- Email entregado
- Email abierto
- Link clickeado
- Email rebotado
- Spam reportado

---

## 🚀 Despliegue

### En tu servidor de producción:

1. **Configurar variables de entorno:**
```bash
export PRODUCTION=True
export EMAIL_HOST=smtp.sendgrid.net
export EMAIL_HOST_PASSWORD=SG.xxxxxx
```

2. **O usar archivo `.env`:**
```bash
# Asegúrate de tener python-decouple instalado
pip install python-decouple

# El proyecto ya está configurado para leerlo
```

3. **Verificar configuración:**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Mensaje de prueba', 'from@email.com', ['to@email.com'])
```

---

## 💰 Costos Comparativos

| Servicio | Plan Gratis | Precio Pagado | Límite Gratis |
|----------|-------------|---------------|---------------|
| **SendGrid** | ✅ Permanente | $19.95/mes (40k emails) | 100/día |
| **Mailgun** | ⚠️ 3 meses | $35/mes (50k emails) | 5,000/mes |
| **Amazon SES** | ✅ Permanente | $0.10 por 1,000 emails | 62k/mes desde EC2 |
| **Gmail** | ❌ No soportado | N/A | 500/día (no recomendado) |

---

## 🎓 Recomendación Final

**Para Selena Shop:**

1. **Desarrollo Local:** Usar `console.EmailBackend` (actual)
2. **Producción:** Usar **SendGrid** con plan gratis
   - 100 emails/día = suficiente para empezar
   - Cuando crezcas, upgrade a plan pagado
   - Profesional y confiable

**Configuración de 5 minutos:**
1. Crear cuenta en SendGrid
2. Crear API Key
3. Agregar a `.env` en producción
4. ¡Listo!

---

## 📞 Soporte

Si tienes problemas configurando el email en producción, revisa:
- Logs de SendGrid Dashboard
- Logs de Django (`python manage.py runserver`)
- Verificación de dominio (mejora deliverability)
- Lista de bloqueo de emails (bounce list)
