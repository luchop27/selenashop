# 📧 Configuración de Resend para Selena Shop

## ✅ Configuración Completada

### API Key Configurada:
```
re_5jwJYjfR_NjHxPi4WQ9GemJqbCcWKyCoz
```

### Configuración en settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = 're_5jwJYjfR_NjHxPi4WQ9GemJqbCcWKyCoz'
DEFAULT_FROM_EMAIL = 'Selena Shop <onboarding@resend.dev>'
```

---

## 🚀 Cómo Probar

### 1. Ejecutar Script de Prueba:
```bash
cd selenashop
python test_resend.py
```

Te pedirá un email y enviará un mensaje de prueba.

### 2. Verificar en Dashboard:
- Ve a: https://resend.com/emails
- Verás el log en tiempo real
- Estado de entrega
- Contenido del email

---

## 📊 Límites de Plan Gratis

| Concepto | Límite |
|----------|--------|
| Emails al mes | 3,000 |
| Emails al día | 100 |
| Duración | Permanente ✅ |

### Si necesitas más:
- **$20/mes**: 50,000 emails/mes
- **Pay as you go**: Desde $1 por 1,000 emails

---

## 🎯 Ventajas de Resend

1. ✅ **Sin problemas SSL** - Funciona en Python 3.11+
2. ✅ **Dashboard moderno** - Logs en tiempo real
3. ✅ **Deliverability alta** - 99% llega a inbox
4. ✅ **Fácil de usar** - Configuración en 5 minutos
5. ✅ **Gratis permanente** - 3,000 emails/mes
6. ✅ **React Email** - Templates modernos (opcional)
7. ✅ **Webhooks** - Tracking de aperturas/clicks

---

## 📧 Configurar Email Personalizado (Opcional)

Por defecto usas: `onboarding@resend.dev`

Para usar tu propio dominio (ej: `noreply@selenashop.com`):

### Paso 1: Agregar Dominio
1. Ve a: https://resend.com/domains
2. Clic en "Add Domain"
3. Ingresa: `selenashop.com`

### Paso 2: Configurar DNS
Agregar estos registros en tu proveedor de dominio:

```
Tipo: TXT
Nombre: @
Valor: [te lo da Resend]

Tipo: TXT  
Nombre: resend._domainkey
Valor: [te lo da Resend]

Tipo: MX
Nombre: @
Valor: feedback-smtp.us-east-1.amazonses.com
Prioridad: 10
```

### Paso 3: Verificar
- Espera 5-10 minutos
- Resend verificará automáticamente
- Cuando esté verificado, cambia en settings.py:

```python
DEFAULT_FROM_EMAIL = 'Selena Shop <noreply@selenashop.com>'
```

---

## 🧪 Testing del Sistema Completo

### Test 1: Email Simple
```bash
python test_resend.py
```

### Test 2: Sistema de Reset de Contraseña
```bash
python test_debug_reset.py
```

### Test 3: En Navegador
1. Ir a: `http://127.0.0.1:8000/usuarios/login/`
2. Clic en "Restablecer contraseña"
3. Ingresar email
4. Verificar que llegue el código

---

## 📈 Monitoreo

### Dashboard de Resend:
- URL: https://resend.com/emails
- Ver logs en tiempo real
- Estadísticas de envío
- Emails entregados/rebotados

### Lo que puedes ver:
- ✅ Estado de cada email
- ✅ Hora de envío
- ✅ Destinatario
- ✅ Contenido completo
- ✅ Errores (si hay)

---

## 🆘 Troubleshooting

### Error: "Invalid API key"
**Solución:** Verifica que la key en settings.py sea exacta:
```python
EMAIL_HOST_PASSWORD = 're_5jwJYjfR_NjHxPi4WQ9GemJqbCcWKyCoz'
```

### Error: "Email address not verified"
**Solución:** 
1. Si usas email personalizado, verifica el dominio
2. O usa `onboarding@resend.dev` (pre-verificado)

### Email no llega
**Verificar:**
1. Dashboard de Resend → Ver estado
2. Carpeta de Spam
3. Email destino correcto
4. Límite diario no excedido (100/día)

### Error de conexión
**Verificar:**
```python
EMAIL_HOST = 'smtp.resend.com'  # Sin https://
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'  # Exactamente 'resend'
```

---

## 🔄 Migración desde Gmail

Ya está hecho ✅

**Antes (Gmail):**
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'marcojaramillo0142@gmail.com'
EMAIL_HOST_PASSWORD = 'vckwtnfrekagrhsn'
```

**Ahora (Resend):**
```python
EMAIL_HOST = 'smtp.resend.com'
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = 're_5jwJYjfR_NjHxPi4WQ9GemJqbCcWKyCoz'
```

---

## 📞 Soporte

- Documentación: https://resend.com/docs
- Dashboard: https://resend.com/emails
- Status: https://status.resend.com
- Support: support@resend.com

---

## ✨ Próximos Pasos

1. ✅ Configuración completada
2. 🔄 **Probar envío** → `python test_resend.py`
3. 🔄 **Probar reset de contraseña** → Navegador
4. 🔄 **Verificar dashboard** → https://resend.com/emails
5. ⏭️ (Opcional) Configurar dominio personalizado
6. ⏭️ (Opcional) Activar webhooks para tracking

---

## 🎉 ¡Listo!

Tu sistema de emails está configurado con Resend y listo para usar.

**Características:**
- ✅ 3,000 emails/mes gratis
- ✅ Sin problemas SSL
- ✅ Dashboard moderno
- ✅ Listo para producción
