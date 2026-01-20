# ==================== NUEVAS VISTAS PARA RESET DE CONTRASEÑA CON CÓDIGO ====================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils import timezone
from apps.usuarios.models import Usuario, PasswordResetCode
import os
import logging
import traceback

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def password_reset_request_code(request):
    """Vista para solicitar código de restablecimiento de contraseña"""
    if request.method == 'POST':
        print(f'\n\n🚀 PASSWORD RESET REQUEST - Método POST')
        print(f'Email recibido: {request.POST.get("email", "").strip()}')
        print('='*60)
        
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Por favor ingresa tu email.')
            return redirect('usuarios:login')
        
        try:
            user = Usuario.objects.get(email=email)
            
            # Invalidar códigos anteriores del usuario
            PasswordResetCode.objects.filter(usuario=user, usado=False).update(usado=True)
            
            # Generar nuevo código de 6 dígitos
            codigo = PasswordResetCode.generar_codigo()
            
            # Crear registro del código
            reset_code = PasswordResetCode.objects.create(
                usuario=user,
                codigo=codigo
            )
            
            # Preparar email
            nombre_usuario = user.nombre or user.email.split('@')[0]
            email_soporte = settings.EMAIL_HOST_USER
            anio_actual = timezone.now().year
            
            # HTML del email
            mensaje_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background-color: #f8f9fa;
                        margin: 0;
                        padding: 20px;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 16px;
                        overflow: hidden;
                        box-shadow: 0 10px 40px rgba(145, 133, 103, 0.15);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #918567 0%, #a89878 100%);
                        padding: 50px 30px;
                        text-align: center;
                    }}
                    .logo-container {{
                        text-align: center;
                        margin-bottom: 25px;
                    }}
                    .logo {{
                        max-width: 150px;
                        height: auto;
                        background: white;
                        padding: 15px;
                        border-radius: 12px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }}
                    .header-title {{
                        color: white;
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header-subtitle {{
                        color: rgba(255,255,255,0.95);
                        margin: 10px 0 0;
                        font-size: 16px;
                    }}
                    .content {{
                        padding: 50px 40px;
                    }}
                    .greeting {{
                        font-size: 20px;
                        color: #333;
                        margin-bottom: 20px;
                        font-weight: 600;
                    }}
                    .message {{
                        color: #555;
                        line-height: 1.8;
                        margin-bottom: 30px;
                        font-size: 16px;
                    }}
                    .code-container {{
                        text-align: center;
                        margin: 40px 0;
                        padding: 30px;
                        background: #f8f9fa;
                        border-radius: 12px;
                        border: 2px dashed #918567;
                    }}
                    .code-label {{
                        color: #666;
                        font-size: 14px;
                        margin-bottom: 15px;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }}
                    .code {{
                        font-size: 48px;
                        font-weight: bold;
                        color: #918567;
                        letter-spacing: 8px;
                        font-family: 'Courier New', monospace;
                        margin: 10px 0;
                    }}
                    .expiry {{
                        color: #dc3545;
                        font-size: 14px;
                        margin-top: 15px;
                        font-weight: 600;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px 20px;
                        margin: 25px 0;
                        border-radius: 4px;
                    }}
                    .warning-title {{
                        color: #856404;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }}
                    .warning-text {{
                        color: #856404;
                        font-size: 14px;
                        margin: 0;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #eee;
                    }}
                    .footer-text {{
                        color: #999;
                        font-size: 14px;
                        margin: 5px 0;
                    }}
                    .link {{
                        color: #918567;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <div class="logo-container">
                            <img src="cid:logoselena" alt="Selena Shop" class="logo">
                        </div>
                        <h1 class="header-title">Recuperación de Contraseña</h1>
                        <p class="header-subtitle">Tu código de verificación está listo</p>
                    </div>
                    
                    <div class="content">
                        <p class="greeting">¡Hola {nombre_usuario}!</p>
                        
                        <p class="message">
                            Recibimos una solicitud para restablecer la contraseña de tu cuenta en Selena Shop.
                            Utiliza el siguiente código de 6 dígitos para continuar:
                        </p>
                        
                        <div class="code-container">
                            <div class="code-label">Tu Código de Verificación</div>
                            <div class="code">{codigo}</div>
                            <div class="expiry">⏱️ Este código expira en 15 minutos</div>
                        </div>
                        
                        <div class="warning">
                            <div class="warning-title">🔒 Información de Seguridad</div>
                            <p class="warning-text">
                                Si no solicitaste este cambio, ignora este correo. Tu contraseña permanecerá sin cambios.
                                Nunca compartas este código con nadie.
                            </p>
                        </div>
                        
                        <p class="message" style="margin-top: 30px;">
                            <strong>¿Cómo usar el código?</strong><br>
                            1. Ingresa el código de 6 dígitos en la pantalla de verificación<br>
                            2. Crea tu nueva contraseña segura<br>
                            3. ¡Listo! Podrás acceder con tu nueva contraseña
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p class="footer-text">
                            <strong>Selena Shop</strong> - Tu tienda de moda favorita
                        </p>
                        <p class="footer-text">
                            ¿Necesitas ayuda? Escríbenos a 
                            <a href="mailto:{email_soporte}" class="link">{email_soporte}</a>
                        </p>
                        <p class="footer-text">
                            © {anio_actual} Selena Shop. Todos los derechos reservados.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Texto plano (fallback)
            mensaje_texto = f"""
            ¡Hola {nombre_usuario}!
            
            Recibimos una solicitud para restablecer tu contraseña en Selena Shop.
            
            Tu código de verificación es: {codigo}
            
            Este código expira en 15 minutos.
            
            Si no solicitaste este cambio, ignora este correo.
            
            Saludos,
            Equipo de Selena Shop
            """
            
            # Enviar email con manejo robusto de errores
            try:
                print(f'\n\n========== ENVIANDO EMAIL ==========')
                print(f'Destino: {email}')
                print(f'Código: {codigo}')
                print(f'Backend: {settings.EMAIL_BACKEND}')
                print(f'Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
                print(f'====================================\n')
                
                logger.info(f'📧 Intentando enviar código de reset a {email}...')
                
                email_message = EmailMultiAlternatives(
                    subject='Código de Recuperación - Selena Shop',
                    body=mensaje_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email_message.attach_alternative(mensaje_html, "text/html")
                
                # Adjuntar logo como imagen embebida
                from email.mime.image import MIMEImage
                logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo', 'logoselena.png')
                if os.path.exists(logo_path):
                    try:
                        with open(logo_path, 'rb') as f:
                            logo_data = f.read()
                            logo_img = MIMEImage(logo_data)
                            logo_img.add_header('Content-ID', '<logoselena>')
                            logo_img.add_header('Content-Disposition', 'inline', filename='logo.png')
                            email_message.attach(logo_img)
                        logger.info('✅ Logo adjuntado correctamente')
                    except Exception as logo_error:
                        logger.warning(f'⚠️  No se pudo adjuntar logo: {logo_error}')
                        # Continuar sin logo
                else:
                    logger.warning(f'⚠️  Logo no encontrado en: {logo_path}')
                
                # Intentar enviar
                resultado = email_message.send()
                
                if resultado > 0:
                    logger.info(f'✅ Email enviado exitosamente a {email}')
                    logger.info(f'   Código generado: {codigo}')
                    logger.info(f'   Backend: {settings.EMAIL_BACKEND}')
                else:
                    logger.warning(f'⚠️  send() retornó {resultado} - posible fallo silencioso')
                    
            except Exception as email_error:
                logger.error('❌ ERROR AL ENVIAR EMAIL:')
                logger.error(f'   Tipo de error: {type(email_error).__name__}')
                logger.error(f'   Mensaje: {str(email_error)}')
                logger.error(f'   Email destino: {email}')
                logger.error(f'   Backend: {settings.EMAIL_BACKEND}')
                logger.error(f'   Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
                logger.error(f'   Traceback completo:')
                logger.error(traceback.format_exc())
                
                # Re-lanzar para que el bloque except principal lo capture
                raise
            
            # Guardar email en sesión para la verificación
            request.session['reset_email'] = email
            request.session['code_sent_at'] = timezone.now().isoformat()
            
            messages.success(request, f'Se ha enviado un código de 6 dígitos a {email}')
            return redirect('usuarios:password_reset_verify')
            
        except Usuario.DoesNotExist:
            logger.warning(f'⚠️  Intento de reset para email no registrado: {email}')
            # Por seguridad, mostramos el mismo mensaje
            messages.success(request, f'Si el email existe, se enviará un código de verificación.')
            return redirect('usuarios:login')
            
        except Exception as e:
            logger.error('❌ ERROR GENERAL EN password_reset_request_code:')
            logger.error(f'   Tipo: {type(e).__name__}')
            logger.error(f'   Mensaje: {str(e)}')
            logger.error(f'   Traceback:')
            logger.error(traceback.format_exc())
            
            # Mostrar error detallado en desarrollo
            if settings.DEBUG:
                error_msg = f'Error: {type(e).__name__} - {str(e)}'
                messages.error(request, error_msg)
            else:
                messages.error(request, 'Ocurrió un error al procesar tu solicitud. Por favor intenta nuevamente.')
            
            return redirect('usuarios:login')
    
    return redirect('usuarios:login')


@require_http_methods(["GET", "POST"])
def password_reset_verify(request):
    """Vista para verificar el código de 6 dígitos"""
    email = request.session.get('reset_email')
    
    if not email:
        messages.error(request, 'Sesión expirada. Por favor solicita un nuevo código.')
        return redirect('usuarios:login')
    
    if request.method == 'POST':
        # Obtener código ingresado (6 campos)
        codigo_ingresado = ''.join([
            request.POST.get(f'code_{i}', '') for i in range(1, 7)
        ])
        
        if len(codigo_ingresado) != 6 or not codigo_ingresado.isdigit():
            messages.error(request, 'Por favor ingresa un código válido de 6 dígitos.')
            return render(request, 'password_reset_verify.html', {'email': email})
        
        try:
            user = Usuario.objects.get(email=email)
            
            # Buscar código válido
            reset_code = PasswordResetCode.objects.filter(
                usuario=user,
                codigo=codigo_ingresado,
                usado=False
            ).order_by('-creado').first()
            
            if not reset_code:
                messages.error(request, 'Código incorrecto. Verifica e intenta nuevamente.')
                return render(request, 'password_reset_verify.html', {'email': email})
            
            if not reset_code.es_valido():
                messages.error(request, 'El código ha expirado. Solicita uno nuevo.')
                return redirect('usuarios:login')
            
            # Código válido - guardar en sesión y redirigir a cambiar contraseña
            request.session['verified_reset_code'] = reset_code.id
            return redirect('usuarios:password_reset_complete')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('usuarios:login')
    
    # GET - mostrar formulario
    try:
        user = Usuario.objects.get(email=email)
        # Obtener el código más reciente para mostrar tiempo restante
        latest_code = PasswordResetCode.objects.filter(
            usuario=user,
            usado=False
        ).order_by('-creado').first()
        
        context = {
            'email': email,
            'tiempo_restante': latest_code.tiempo_restante() if latest_code else 0
        }
        
        return render(request, 'password_reset_verify.html', context)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('usuarios:login')


@require_http_methods(["GET", "POST"])
def password_reset_complete(request):
    """Vista para establecer la nueva contraseña"""
    code_id = request.session.get('verified_reset_code')
    
    if not code_id:
        messages.error(request, 'Sesión expirada. Por favor solicita un nuevo código.')
        return redirect('usuarios:login')
    
    try:
        reset_code = PasswordResetCode.objects.get(id=code_id, usado=False)
        
        if not reset_code.es_valido():
            messages.error(request, 'El código ha expirado. Solicita uno nuevo.')
            return redirect('usuarios:login')
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if not password1 or not password2:
                messages.error(request, 'Por favor completa todos los campos.')
                return render(request, 'password_reset_complete.html')
            
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'password_reset_complete.html')
            
            if len(password1) < 6:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return render(request, 'password_reset_complete.html')
            
            # Cambiar contraseña
            user = reset_code.usuario
            user.set_password(password1)
            user.save()
            
            # Marcar código como usado
            reset_code.usado = True
            reset_code.save()
            
            # Limpiar sesión
            if 'reset_email' in request.session:
                del request.session['reset_email']
            if 'verified_reset_code' in request.session:
                del request.session['verified_reset_code']
            if 'code_sent_at' in request.session:
                del request.session['code_sent_at']
            
            messages.success(request, '¡Contraseña cambiada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('usuarios:login')
        
        return render(request, 'password_reset_complete.html')
        
    except PasswordResetCode.DoesNotExist:
        messages.error(request, 'Código inválido.')
        return redirect('usuarios:login')


@require_http_methods(["POST"])
def password_reset_resend(request):
    """Vista para reenviar el código de verificación"""
    email = request.session.get('reset_email')
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Sesión expirada'})
    
    try:
        user = Usuario.objects.get(email=email)
        
        # Verificar que no se abuse del reenvío (máximo 1 por minuto)
        last_code = PasswordResetCode.objects.filter(
            usuario=user
        ).order_by('-creado').first()
        
        if last_code:
            from datetime import timedelta
            time_since_last = timezone.now() - last_code.creado
            if time_since_last < timedelta(seconds=60):
                segundos_restantes = 60 - int(time_since_last.total_seconds())
                return JsonResponse({
                    'success': False,
                    'message': f'Espera {segundos_restantes} segundos antes de solicitar un nuevo código'
                })
        
        # Invalidar códigos anteriores
        PasswordResetCode.objects.filter(usuario=user, usado=False).update(usado=True)
        
        # Generar nuevo código
        codigo = PasswordResetCode.generar_codigo()
        reset_code = PasswordResetCode.objects.create(
            usuario=user,
            codigo=codigo
        )
        
        # Enviar email (reutilizando la misma lógica)
        nombre_usuario = user.nombre or user.email.split('@')[0]
        
        mensaje_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #918567 0%, #a89878 100%); padding: 30px; text-align: center; border-radius: 10px; color: white;">
                <h1 style="margin: 0; font-size: 24px;">Nuevo Código de Verificación</h1>
                <p style="margin: 10px 0 0;">Selena Shop</p>
            </div>
            <div style="padding: 30px 20px; background: white; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <p style="font-size: 16px; color: #333;">¡Hola {nombre_usuario}!</p>
                <p style="color: #666;">Solicitaste un nuevo código de verificación. Aquí está:</p>
                <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; margin: 20px 0; border: 2px dashed #918567;">
                    <p style="font-size: 12px; color: #666; margin: 0 0 10px;">TU CÓDIGO</p>
                    <p style="font-size: 36px; font-weight: bold; color: #918567; letter-spacing: 5px; margin: 0; font-family: monospace;">{codigo}</p>
                    <p style="font-size: 12px; color: #dc3545; margin: 10px 0 0;">Expira en 15 minutos</p>
                </div>
                <p style="color: #666; font-size: 14px;">Si no solicitaste este código, ignora este correo.</p>
            </div>
        </body>
        </html>
        """
        
        mensaje_texto = f"Hola {nombre_usuario},\n\nTu nuevo código de verificación es: {codigo}\n\nExpira en 15 minutos.\n\nSelena Shop"
        
        # Enviar email con manejo de errores
        try:
            logger.info(f'📧 Reenviando código a {user.email}...')
            
            from django.core.mail import EmailMultiAlternatives
            email_message = EmailMultiAlternatives(
                subject='Nuevo Código de Recuperación - Selena Shop',
                body=mensaje_texto,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_message.attach_alternative(mensaje_html, "text/html")
            
            resultado = email_message.send()
            
            if resultado > 0:
                logger.info(f'✅ Código reenviado exitosamente a {user.email}')
                logger.info(f'   Nuevo código: {codigo}')
            else:
                logger.warning(f'⚠️  Reenvío retornó {resultado}')
                
        except Exception as email_error:
            logger.error('❌ ERROR AL REENVIAR CÓDIGO:')
            logger.error(f'   Tipo: {type(email_error).__name__}')
            logger.error(f'   Mensaje: {str(email_error)}')
            logger.error(f'   Traceback:')
            logger.error(traceback.format_exc())
            
            return JsonResponse({
                'success': False,
                'message': f'Error al enviar email: {str(email_error)}'
            }, status=500)
        
        # Actualizar sesión
        request.session['code_sent_at'] = timezone.now().isoformat()
        
        return JsonResponse({
            'success': True,
            'message': 'Nuevo código enviado a tu email'
        })
        
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuario no encontrado'})
