# ✨ Integración WhatsApp Business API - RESUMEN RÁPIDO

## 📍 Archivos Creados/Modificados

| Archivo | Cambio | Descripción |
|---------|--------|-------------|
| `selenashop/settings.py` | ✏️ Modificado | Agregadas credenciales de Meta WhatsApp |
| `core/whatsapp_utils.py` | ✨ Creado | Funciones para enviar mensajes a WhatsApp |
| `core/views.py` | ✏️ Modificado | Integración en `checkout_process()` |
| `test_whatsapp.py` | ✨ Creado | Script para probar la configuración |
| `WHATSAPP_SETUP.md` | ✨ Creado | Guía completa de configuración |

## 🚀 Inicio Rápido (3 Pasos)

### Paso 1️⃣: Obtén los Tokens de Meta
1. Ve a [Meta Business Console](https://business.facebook.com)
2. WhatsApp Manager → Copia **Phone Number ID**
3. Desarrolladores → Copia **Access Token**

### Paso 2️⃣: Configura Django
Edita `selenashop/settings.py` y reemplaza:

```python
WHATSAPP_PHONE_NUMBER_ID = 'TU_PHONE_NUMBER_ID_AQUI'
WHATSAPP_ACCESS_TOKEN = 'TU_ACCESS_TOKEN_AQUI'
WHATSAPP_ADMIN_NUMBER = '+593979607739'
```

### Paso 3️⃣: ¡Prueba!
```bash
python test_whatsapp.py
```

## 📱 ¿Cómo Funciona?

```
Cliente → Llena Checkout → Presiona "Realizar Pedido"
    ↓
Django Backend:
  • Crea el Pedido
  • Formatea el mensaje
  • Envía a WhatsApp API de Meta
  ↓
Admin recibe en WhatsApp:
  "✨ NUEVO PEDIDO #ORD-20250214-ABCD ✨
   👤 Nombre: Luis Alberto Vasquez
   📊 Detalles del producto...
   💰 Total: $40.00"
```

## 🎯 Características

✅ **Automático** - Sin intervención del usuario
✅ **Seguro** - Usa API oficial de Meta
✅ **Personalizable** - Edita el formato en `whatsapp_utils.py`
✅ **Robusto** - Manejo de errores completo
✅ **Fallback** - Genera links de WhatsApp Web si falla API

## 🔧 Personalización

### Cambiar el Formato del Mensaje

Edita la función `formatear_mensaje_pedido()` en `core/whatsapp_utils.py`:

```python
def formatear_mensaje_pedido(pedido):
    mensaje = f"""✨ *NUEVO PEDIDO #{pedido.numero_pedido}* ✨
...
```

Puedes agregar:
- Emojis personalizados
- Links de seguimiento
- Horarios de atención
- Información adicional

### Enviar a Múltiples Admin

Edita `checkout_process()` en `core/views.py`:

```python
# Enviar a admin principal
resultado1 = enviar_notificacion_pedido(pedido)

# Enviar a segundo admin
resultado2 = enviar_mensaje_whatsapp(
    '+593987654321',  # Otro admin
    formatear_mensaje_pedido(pedido)
)
```

## 🐛 Debugging

Ver logs en la consola del servidor:

```
✅ WhatsApp: Mensaje enviado exitosamente. ID: wamid.xxxx
❌ WhatsApp: Error 401. Token inválido
```

## ⚠️ Problemas Comunes

| Problema | Solución |
|----------|----------|
| "No configurado" | Verifica `settings.py` no tenga valores `YOUR_*` |
| "Error 401" | Access Token expiró, genera uno nuevo en Meta |
| "Error 400" | Número sin formato internacional (+593...) |
| "Mensaje no llega" | Espera 24h, requiere que el admin haya abierto chat antes |

## 📞 Soporte

- **Documentación Completa**: Revisa `WHATSAPP_SETUP.md`
- **Script de Prueba**: Ejecuta `python test_whatsapp.py`
- **Logs**: Revisa consola del servidor Django

## 📝 Próximos Pasos Opcionales

- [ ] Agregar notificación cuando se actualiza estado del pedido
- [ ] Enviar comprobante de pago por WhatsApp
- [ ] Agregar seguimiento de envío en tiempo real
- [ ] Responder automáticamente algunas preguntas frecuentes

---

**¿Todo configurado?** 🎉

Realiza un pedido de prueba en el checkout y verifica que recibes el mensaje en WhatsApp.
