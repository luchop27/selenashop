# ❓ PREGUNTAS Y RESPUESTAS - CREDENCIALES WHATSAPP

## P: ¿De dónde exactamente obtengo el Access Token?

**R:** 
1. Ve a: https://developers.facebook.com/
2. Click "Mis apps" → Tu app
3. Selecciona: WhatsApp → Configuración
4. En el menú izquierdo: "Credenciales"
5. Busca "Tokens de acceso"
6. Click "Generar token"
7. Se mostrará un código largo → **Cópialo**

---

## P: ¿Cuál es el Phone Number ID?

**R:**
1. Ve a: WhatsApp → Números de teléfono
2. Busca tu número (ej: +593 979607739)
3. Haz click en él
4. Se mostrarán los detalles
5. Busca: "ID del número de teléfono"
6. Copia ese número (es solo dígitos, ej: 102345678901234)

---

## P: ¿Y el Business Account ID?

**R:**
1. Ve a: WhatsApp → Configuración
2. En el menú izquierdo: "Información general"
3. Busca: "ID de cuenta" o "Business Account ID"
4. Cópialo (también es solo dígitos)

---

## P: ¿Cuántos caracteres tiene cada uno?

**R:**
- **Access Token**: Muy largo (100-200+ caracteres)
- **Phone Number ID**: 12-15 dígitos
- **Business Account ID**: 15 dígitos

---

## P: ¿Los caracteres pueden tener espacios?

**R:** No, cópialos SIN espacios. Si ves espacios en Meta, ignóralos.

---

## P: ¿Debo copiar el símbolo + del teléfono?

**R:** No, solo los números. Si ves:
```
+593 979607739
```
Copia:
```
593979607739
```

---

## P: ¿Se pueden ver los tokens de otros?

**R:** NO. Nunca compartas tus tokens. Son secretos como contraseñas.

---

## P: ¿Qué pasa si publico mis tokens por error?

**R:** 
1. Accede a Meta inmediatamente
2. Regenera nuevos tokens
3. Los viejos dejan de funcionar
4. Actualiza settings.py con los nuevos

---

## P: ¿Puedo usar el token de alguien más?

**R:** No funcionará. Cada token está vinculado a una cuenta Meta específica.

---

## P: ¿Cuánto tiempo tarda en obtenerlos?

**R:** 5-10 minutos máximo.

---

## P: ¿Necesito una cuenta de negocio especial?

**R:** No, una cuenta Meta normal funciona. Solo necesitas:
- Acceso a Meta Developers
- Permiso para crear apps (que tienes por default)
- Un número de WhatsApp Business

---

## P: ¿Cómo obtengo un número de WhatsApp Business?

**R:**
1. En WhatsApp → Números de teléfono
2. Click "Agregar número"
3. Ingresa tu número (ej: 0979607739)
4. WhatsApp te enviará un código en la app
5. Confirma el código
6. ¡Listo! Aparecerá en la lista

---

## P: ¿El número tiene que ser el del admin?

**R:** No necesariamente. Puedes usar cualquier número. En el ejemplo usamos 0979607739, pero puede ser cualquiera que tengas disponible.

---

## P: ¿Puedo cambiar el número después?

**R:** Sí. En settings.py hay:
```python
WHATSAPP_ADMIN_NUMBER = '593979607739'
```
Cámbialo cuando quieras.

---

## P: ¿Hay costos asociados?

**R:** Meta tiene un modelo de precios para mensajes. Revisa https://developers.facebook.com/docs/whatsapp/pricing

---

## P: ¿Hay un límite de mensajes?

**R:** Depende de tu plan. La mayoría de planes tienen límites iniciales, pero puedes aumentarlos.

---

## P: ¿Puedo probar sin credenciales reales?

**R:** Sí, el sistema tiene modo de prueba. Los tests funcionan sin credenciales.

---

## P: ¿Dónde pego exactamente las credenciales?

**R:**
1. Abre: `selenashop/settings.py`
2. Presiona Ctrl+F
3. Busca: `WHATSAPP_ACCESS_TOKEN`
4. Encontrarás:
```python
WHATSAPP_ACCESS_TOKEN = ''
WHATSAPP_PHONE_NUMBER_ID = ''
WHATSAPP_BUSINESS_ACCOUNT_ID = ''
WHATSAPP_ADMIN_NUMBER = '593979607739'
```
5. Pega entre las comillas:
```python
WHATSAPP_ACCESS_TOKEN = 'EAABsbCS1iHgBAOZCZBu2kP7...'
WHATSAPP_PHONE_NUMBER_ID = '102345678901234'
WHATSAPP_BUSINESS_ACCOUNT_ID = '123456789012345'
```

---

## P: ¿Cómo verifico que pegué correctamente?

**R:** Ejecuta:
```bash
python test_whatsapp_complete.py
```

Si ves:
```
✅ SISTEMA LISTO PARA PRODUCCIÓN
```

¡Está correcto!

---

## P: ¿Qué pasa si no pego nada?

**R:** El sistema seguirá funcionando pero sin enviar WhatsApp. Los pedidos se crearán normalmente.

---

## P: ¿Hay un archivo de ejemplo?

**R:** Sí, `WHATSAPP_CONFIG_EXAMPLE.txt` tiene un ejemplo con valores ficticios.

---

## P: ¿Hay una guía paso a paso?

**R:** Sí:
- `COMO_OBTENER_CREDENCIALES.md` - Paso a paso completo
- `GUIA_VISUAL_CREDENCIALES.md` - Con pantallas
- `WHATSAPP_QUICK_START.md` - Lo más rápido

---

## P: ¿Qué hago si me pierdo?

**R:** Lee en este orden:
1. `COMO_OBTENER_CREDENCIALES.md`
2. `GUIA_VISUAL_CREDENCIALES.md`
3. Este archivo (FAQ)

---

## TLDR (Muy Resumen)

```
1. Ve a: https://developers.facebook.com/
2. Copia 3 cosas de ahí:
   - Access Token (en Configuración → Credenciales → Generar)
   - Phone Number ID (en Números de teléfono)
   - Business Account ID (en Configuración → Información)
3. Pégalas en: selenashop/settings.py (al final)
4. Guarda (Ctrl+S)
5. Prueba: python test_whatsapp_complete.py
6. ¡Listo!
```

---

**¿Aún tienes dudas?** Revisa los archivos de documentación mencionados arriba.
