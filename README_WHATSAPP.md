# 📱 WHATSAPP NOTIFICATIONS - VÓRTICE ECUADOR

> Recibe notificaciones automáticas en WhatsApp cuando tus clientes realizan pedidos

## 🎯 ¿Qué hace?

Cuando un cliente finaliza la compra en tu tienda:

```
1. Cliente completa el checkout
        ↓
2. Click en "Realizar Pedido"
        ↓
3. Sistema crea el pedido
        ↓
4. 📨 AUTOMÁTICAMENTE se envía WhatsApp al admin con:
        - Datos del cliente
        - Productos solicitados
        - Resumen de precios
        - Ciudad de envío
```

---

## 📱 Ejemplo de Mensaje Recibido

```
✨ *Pedido ORD-20240108-ABCD - Vórtice Ecuador* ✨
--------------------------------------
📋 *Datos del Cliente:*
👤 Nombre: Luis Alberto Vasquez Gomez
📧 Correo: xkrules.2005@gmail.com
📱 Teléfono: 0979607739
🏙️ Ciudad: Quito
🏠 Dirección: Kleber Franco
--------------------------------------
📦 *Detalles del pedido:*

🔹 *Camiseta V-N002*
   🔸 Talla: U
   🔸 Color: Rojo
   🔸 Cantidad: 1
   🔸 Precio unitario: $35.00
   🔸 Subtotal: $35.00

--------------------------------------
💰 *Resumen del pedido:*
🛍️ Subtotal: $35.00
🚚 Costo de envío: $5.00
✅ *Total a pagar: $40.00*
--------------------------------------

¡Gracias! 😊

🛍️ *Vórtice Ecuador - Moda con estilo*
```

---

## 🚀 Quick Start (3 pasos)

### 1️⃣ Obtener Credenciales de Meta

- Ir a: https://developers.facebook.com/
- Crear app → Agregar WhatsApp Business
- Copiar: Access Token, Phone Number ID, Business Account ID

### 2️⃣ Actualizar Configuración

En `selenashop/settings.py`, ir al final y actualizar:

```python
WHATSAPP_ACCESS_TOKEN = 'TU_TOKEN_AQUI'
WHATSAPP_PHONE_NUMBER_ID = 'TU_PHONE_ID_AQUI'
WHATSAPP_BUSINESS_ACCOUNT_ID = 'TU_BUSINESS_ID_AQUI'
WHATSAPP_ADMIN_NUMBER = '593979607739'
```

### 3️⃣ Probar

```bash
python test_whatsapp_complete.py
```

**¡Eso es! Sistema listo.** 🎉

---

## 📁 Archivos de Documentación

| Archivo | Para Quién | Contenido |
|---------|-----------|----------|
| **WHATSAPP_IMPLEMENTATION.md** | 👨‍💼 Gerente | Instrucciones simples y amigables |
| **WHATSAPP_SETUP_GUIDE.md** | 👨‍💻 Desarrollador | Configuración técnica detallada |
| **RESUMEN_WHATSAPP_INTEGRATION.md** | 📚 Documentación | Resumen de cambios y arquitectura |
| **test_whatsapp_complete.py** | 🧪 Testing | Script de validación completa |

---

## 🏗️ Tecnología

- **API**: Meta WhatsApp Business API
- **Base URL**: `https://graph.instagram.com/v18.0`
- **Autenticación**: Access Token
- **Método**: HTTP POST
- **Formato**: JSON

---

## ✅ Características

- ✅ **Automático**: Sin intervención manual
- ✅ **No bloquea**: No afecta el proceso de compra
- ✅ **Robusto**: Manejo completo de errores
- ✅ **Informativo**: Incluye todos los detalles
- ✅ **Bonito**: Con emojis y formato
- ✅ **Seguro**: Credenciales en variables de entorno

---

## 🔒 Seguridad

### NO hagas esto:

```python
# ❌ MAL - Credenciales en código
WHATSAPP_ACCESS_TOKEN = 'EAABsbCS1iHgBAOZCZBu2kP7...'
```

### Haz esto:

```python
# ✅ BIEN - Usa variables de entorno
import os
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
```

---

## 📊 Estructura

```
Checkout
   ↓
checkout_process() en core/views.py
   ↓
Crear Pedido
   ↓
Preparar datos
   ↓
enviar_notificacion_pedido() en core/whatsapp.py
   ↓
WhatsAppAPI.enviar_mensaje_pedido()
   ↓
HTTP POST a Meta API
   ↓
📱 Mensaje en WhatsApp del admin
```

---

## 🧪 Pruebas

### Test de Credenciales

```bash
python test_whatsapp_integration.py
```

**Muestra:**
- ✅ Estado de credenciales
- ✅ Ejemplo de mensaje

### Test Completo

```bash
python test_whatsapp_complete.py
```

**Valida:**
- ✅ Credenciales configuradas
- ✅ Instancia de API
- ✅ Formateo de mensaje
- ✅ Estructura correcta
- ✅ Emojis incluidos

---

## 🐛 Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| "Credenciales no configuradas" | `WHATSAPP_ACCESS_TOKEN` vacío | Pegar token en settings.py |
| "Mensaje no llega" | Token/número inválido | Validar en Meta |
| "401 Unauthorized" | Token expiró | Generar nuevo en Meta |
| "Invalid recipient" | Número no registrado | Validar en WhatsApp Business |

---

## 📚 Referencias

- **Meta Developers**: https://developers.facebook.com/
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp/cloud-api

---

## 📝 Cambios Realizados

### Nuevo Módulo
- `core/whatsapp.py` - Integración completa

### Modificaciones
- `core/views.py` - Llamada en `checkout_process()`
- `selenashop/settings.py` - Configuración
- `requirements.txt` - Agregado `requests`

### Documentación
- `WHATSAPP_SETUP_GUIDE.md` - Guía técnica
- `WHATSAPP_IMPLEMENTATION.md` - Guía usuario
- `RESUMEN_WHATSAPP_INTEGRATION.md` - Resumen cambios
- Este README

---

## 💡 Notas

- El mensaje se envía de **forma asíncrona** (no bloquea checkout)
- Si falla WhatsApp, el **pedido se crea igual**
- Se puede usar **número diferente** para test/producción
- **Límite de API**: Revisar plan de Meta

---

## 🎉 Ready to Go!

```
✅ Código implementado
✅ Tests completados
✅ Documentación incluida
✅ Seguridad considerada

Solo falta:
→ Obtener credenciales de Meta
→ Actualizar settings.py
→ ¡Probar! 🚀
```

---

**Last Updated**: 8 de Diciembre 2024  
**Status**: ✅ Production Ready  
**Version**: 1.0
