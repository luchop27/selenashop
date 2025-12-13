# 🚀 GUÍA RÁPIDA - ACTIVAR WHATSAPP EN 5 MINUTOS

**Última actualización**: 8 de Diciembre 2024

---

## ✅ Lo que ya está hecho

El sistema completo está implementado y listo. Solo necesitas configurar credenciales.

```
✅ Módulo de WhatsApp creado
✅ Integración en checkout lista
✅ Tests completados y pasados
✅ Documentación incluida
```

---

## 🎯 Tarea: Obtener Credenciales de Meta

### Paso 1: Acceder a Meta Developers

1. Ir a: **https://developers.facebook.com/**
2. Click en "Mis apps" en la esquina superior derecha
3. Click en "Crear app"

### Paso 2: Crear la App

1. Tipo: Seleccionar **"Comercio"**
2. Click en "Siguiente"
3. Llenar información básica
4. Click en "Crear app"

### Paso 3: Agregar WhatsApp

1. En el dashboard, buscar **"WhatsApp"**
2. Click en **"Configurar"** o **"Agregar producto"**
3. Seguir el flujo de setup de WhatsApp

### Paso 4: Obtener Credenciales

En el panel de WhatsApp, encontrarás:

```
1. ACCESS TOKEN
   - Ir a: "Configuración" → "Credenciales"
   - Click "Generar Token"
   - Copiar el token completo

2. PHONE NUMBER ID
   - Ir a: "Números de teléfono"
   - Buscar tu número de WhatsApp Business
   - Copiar "ID del número de teléfono"

3. BUSINESS ACCOUNT ID
   - Ir a: "Configuración"
   - Buscar "ID de cuenta de empresa"
   - Copiar el ID
```

**Ejemplo de cómo lucen:**
```
ACCESS_TOKEN: EAABsbCS1iHgBAOZCZBu2kP7PNZBz...
PHONE_NUMBER_ID: 102345678901234
BUSINESS_ACCOUNT_ID: 123456789012345
```

---

## ⚙️ Configurar el Sistema

### Paso 1: Abrir settings.py

Abrir archivo: `selenashop/settings.py`

Ir al **final del archivo** y buscar:
```python
# ==================== CONFIGURACIÓN WHATSAPP BUSINESS API (META) ====================

WHATSAPP_ACCESS_TOKEN = ''
WHATSAPP_PHONE_NUMBER_ID = ''
WHATSAPP_BUSINESS_ACCOUNT_ID = ''
WHATSAPP_ADMIN_NUMBER = '593979607739'
```

### Paso 2: Pegar Credenciales

```python
WHATSAPP_ACCESS_TOKEN = 'EAABsbCS1iHgBAOZCZBu2kP7PNZBz...'  # ← TU TOKEN AQUI
WHATSAPP_PHONE_NUMBER_ID = '102345678901234'  # ← TU PHONE ID AQUI
WHATSAPP_BUSINESS_ACCOUNT_ID = '123456789012345'  # ← TU BUSINESS ID AQUI
WHATSAPP_ADMIN_NUMBER = '593979607739'  # ← DEJAR IGUAL
```

### Paso 3: Guardar

- Guardar el archivo (Ctrl+S)
- No necesitas reiniciar Django
- ¡Listo!

---

## 🧪 Probar que Funciona

En terminal, ejecutar:

```bash
python test_whatsapp_complete.py
```

Si ves esto, está correctamente configurado:
```
✅ TODOS LOS TESTS PASARON - SISTEMA LISTO PARA PRODUCCIÓN
```

Si no, probablemente algo en la configuración no está bien. Revisar credenciales.

---

## 🧪 Prueba Real

1. Acceder a: `http://localhost:8000/checkout/`
2. Completa el formulario con datos de prueba
3. Click en **"Realizar Pedido"**
4. Verifica que el mensaje llegue a tu WhatsApp

**Ejemplo de lo que debería llegar:**
```
✨ *Pedido ORD-20240108-ABCD - Vórtice Ecuador* ✨
--------------------------------------
📋 *Datos del Cliente:*
👤 Nombre: Tu Nombre
📧 Correo: tu@email.com
...
```

---

## 🔒 Seguridad (IMPORTANTE)

### NO hagas esto:
```python
# ❌ NO COMMITS CON CREDENCIALES REALES
WHATSAPP_ACCESS_TOKEN = 'EAABsbCS1iHgBAOZCZBu2kP7...'
```

### Para Producción, usa .env:

1. Crear archivo `.env` en la raíz:
   ```
   WHATSAPP_ACCESS_TOKEN=tu_token_aqui
   WHATSAPP_PHONE_NUMBER_ID=tu_phone_id_aqui
   WHATSAPP_BUSINESS_ACCOUNT_ID=tu_business_id_aqui
   ```

2. Agregar `.env` a `.gitignore`

3. En `settings.py`:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
   WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
   WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
   ```

4. Instalar:
   ```bash
   pip install python-dotenv
   ```

---

## ❓ Problemas Comunes

### "Credenciales no configuradas"
→ Revisar que los valores en settings.py no estén vacíos

### "El mensaje no llega"
→ 1. Verificar credenciales en Meta
→ 2. Validar número en WhatsApp Business
→ 3. Ejecutar: `python test_whatsapp_complete.py`

### "Error 401 Unauthorized"
→ Token expiró, generar uno nuevo en Meta

### "Invalid recipient"
→ Número no validado, ir a Meta y validarlo

---

## 📞 Números de Teléfono Validados

En Meta, necesitas validar el número de teléfono del admin:

1. Ir a: "Números de teléfono" en Meta
2. Buscar el número: **0979607739**
3. Si no está, agregar uno
4. WhatsApp enviará código de verificación
5. Confirmar código en la app de WhatsApp

---

## ✅ Checklist Final

- [ ] Accedí a Meta Developers
- [ ] Creé una app
- [ ] Agregué WhatsApp Business
- [ ] Obtuve Access Token
- [ ] Obtuve Phone Number ID
- [ ] Obtuve Business Account ID
- [ ] Actualicé settings.py
- [ ] Ejecuté test_whatsapp_complete.py
- [ ] Realicé pedido de prueba
- [ ] Recibí mensaje en WhatsApp

---

## 📚 Documentación Completa

Para más detalles:
- `WHATSAPP_IMPLEMENTATION.md` - Guía completa
- `WHATSAPP_SETUP_GUIDE.md` - Configuración técnica
- `README_WHATSAPP.md` - Visión general

---

## 🎉 ¡Listo!

Una vez configurado, el sistema enviará automáticamente mensajes de WhatsApp cada vez que:
- ✅ Un cliente realiza un pedido
- ✅ Incluye todos los detalles
- ✅ Con formato bonito y emojis
- ✅ Sin intervención manual

**¡No hay nada más que hacer! El sistema funciona automáticamente.** 🚀

---

**Tiempo estimado**: 5 minutos  
**Dificultad**: Fácil ⭐
