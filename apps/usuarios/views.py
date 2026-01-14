from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import Usuario, EmailVerificationToken
import base64
import os


def obtener_logo_base64():
    """Convierte el logo a base64 para usar en emails"""
    try:
        logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'static', 'images', 'logo', 'logoselena.png')
        if not os.path.exists(logo_path):
            # Intentar ruta alternativa
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo', 'logoselena.png')
        
        with open(logo_path, 'rb') as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error cargando logo: {e}")
        return ""


def enviar_email_directo(destinatario, asunto, mensaje_html, incluir_logo=True):
    """
    Función para enviar emails usando smtplib directamente con SSL
    Evita problemas de certificados en Windows
    Adjunta el logo como imagen embebida usando Content-ID
    """
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    
    try:
        print(f"🔧 Iniciando envío de email a {destinatario}")
        print(f"📧 Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"👤 Usuario: {settings.EMAIL_HOST_USER}")
        
        # Crear contexto SSL que no verifica certificados
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        print("✅ Contexto SSL creado (sin verificación de certificados)")
        
        # Crear mensaje con partes relacionadas (para imágenes embebidas)
        msg = MIMEMultipart('related')
        msg['Subject'] = asunto
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = destinatario
        
        # Crear parte alternativa para HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Agregar versión HTML
        html_part = MIMEText(mensaje_html, 'html', 'utf-8')
        msg_alternative.attach(html_part)
        
        # Adjuntar logo como imagen embebida
        if incluir_logo:
            try:
                logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'static', 'images', 'logo', 'logoselena.png')
                if not os.path.exists(logo_path):
                    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo', 'logoselena.png')
                
                with open(logo_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img = MIMEImage(img_data, 'png')
                    img.add_header('Content-ID', '<logoselena>')
                    img.add_header('Content-Disposition', 'inline', filename='logoselena.png')
                    msg.attach(img)
                    print("✅ Logo adjuntado como imagen embebida")
            except Exception as e:
                print(f"⚠️ No se pudo adjuntar el logo: {e}")
        
        print("✅ Mensaje creado")
        
        # Conectar y enviar
        print(f"🔌 Conectando a {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as server:
            print("✅ Conexión establecida")
            
            print("🔐 Autenticando...")
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print("✅ Autenticación exitosa")
            
            print("📤 Enviando mensaje...")
            server.sendmail(settings.EMAIL_HOST_USER, destinatario, msg.as_string())
            print("✅ Mensaje enviado")
        
        print(f"✅✅✅ Email enviado exitosamente a {destinatario}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación: {e}")
        print("⚠️ Verifica que:")
        print("   1. La verificación en 2 pasos esté activada en Gmail")
        print("   2. Hayas generado una 'Contraseña de aplicación' en https://myaccount.google.com/apppasswords")
        print("   3. La contraseña sea exactamente 16 caracteres SIN ESPACIOS")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {e}")
        return False
    except ssl.SSLError as e:
        print(f"❌ Error SSL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general enviando email: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def enviar_email_verificacion(request, usuario):
    """Envía el correo de verificación de email"""
    try:
        # Crear token de verificación (se genera automáticamente en save())
        token_obj = EmailVerificationToken.objects.create(usuario=usuario)
        
        # Construir URL de verificación
        verify_url = request.build_absolute_uri(
            f'/verificar-email/{token_obj.token}/'
        )
        
        # Usar CID para el logo (Content-ID)
        logo_src = "cid:logoselena"
        
        nombre_usuario = usuario.nombre or usuario.email.split('@')[0]
        
        # Preparar el correo HTML profesional con el color de marca #918567
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
                    font-size: 32px;
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
                    font-size: 22px;
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
                .btn-container {{
                    text-align: center;
                    margin: 40px 0;
                }}
                .btn {{
                    display: inline-block;
                    background: linear-gradient(135deg, #918567 0%, #a89878 100%);
                    color: white !important;
                    padding: 18px 50px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: bold;
                    font-size: 16px;
                    box-shadow: 0 8px 20px rgba(145, 133, 103, 0.3);
                    transition: all 0.3s ease;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 12px 24px rgba(145, 133, 103, 0.4);
                }}
                .features {{
                    background: linear-gradient(to bottom, #faf9f7, #ffffff);
                    border: 2px solid #f0ebe3;
                    padding: 30px;
                    border-radius: 12px;
                    margin: 30px 0;
                }}
                .features h3 {{
                    color: #918567;
                    margin: 0 0 20px;
                    font-size: 18px;
                }}
                .feature-item {{
                    display: flex;
                    align-items: center;
                    margin: 15px 0;
                }}
                .feature-icon {{
                    font-size: 24px;
                    margin-right: 15px;
                    min-width: 30px;
                }}
                .feature-text {{
                    color: #666;
                    font-size: 15px;
                }}
                .divider {{
                    height: 1px;
                    background: linear-gradient(to right, transparent, #d4cfc4, transparent);
                    margin: 30px 0;
                }}
                .footer {{
                    background: linear-gradient(to bottom, #faf9f7, #f5f3f0);
                    padding: 30px;
                    text-align: center;
                    border-top: 2px solid #e8e3da;
                }}
                .footer-text {{
                    color: #999;
                    font-size: 13px;
                    margin: 5px 0;
                }}
                .footer-text a {{
                    color: #918567;
                    text-decoration: none;
                }}
                .link-alternative {{
                    margin-top: 20px;
                    padding: 15px;
                    background: #faf9f7;
                    border: 1px solid #e8e3da;
                    border-radius: 8px;
                    word-break: break-all;
                }}
                .link-alternative p {{
                    color: #888;
                    font-size: 12px;
                    margin: 0 0 10px;
                }}
                .link-alternative a {{
                    color: #918567;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo-container">
                        <img src="{logo_src}" alt="Selena Shop" class="logo">
                    </div>
                    <h1 class="header-title">🎉 ¡Bienvenido!</h1>
                    <p class="header-subtitle">Tu cuenta ha sido creada exitosamente</p>
                </div>
                
                <div class="content">
                    <p class="greeting">Hola <strong>{nombre_usuario}</strong>,</p>
                    
                    <p class="message">
                        ¡Gracias por unirte a <strong>Selena Shop</strong>! Estamos emocionados de tenerte como parte de nuestra comunidad de moda. 
                        Para completar tu registro y desbloquear todas las funciones, por favor verifica tu dirección de correo electrónico.
                    </p>
                    
                    <div class="btn-container">
                        <a href="{verify_url}" class="btn">
                            ✨ Verificar mi Email
                        </a>
                    </div>
                    
                    <div class="features">
                        <h3>🌟 Beneficios de tu cuenta verificada:</h3>
                        <div class="feature-item">
                            <span class="feature-icon">🛍️</span>
                            <span class="feature-text">Acceso completo a nuestro catálogo exclusivo</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📦</span>
                            <span class="feature-text">Seguimiento de pedidos en tiempo real</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🎁</span>
                            <span class="feature-text">Ofertas exclusivas y descuentos especiales</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">💳</span>
                            <span class="feature-text">Proceso de compra rápido y seguro</span>
                        </div>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <div class="link-alternative">
                        <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                        <a href="{verify_url}">{verify_url}</a>
                    </div>
                    
                    <p style="color: #999; font-size: 13px; margin-top: 30px; text-align: center;">
                        Este enlace expira en 48 horas.
                    </p>
                </div>
                
                <div class="footer">
                    <p class="footer-text">Este correo fue enviado automáticamente. Por favor no respondas.</p>
                    <p class="footer-text">© 2026 Selena Shop - Todos los derechos reservados</p>
                    <p class="footer-text" style="margin-top: 15px;">
                        ¿Necesitas ayuda? <a href="mailto:soporte@selenashop.com">Contáctanos</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enviar correo
        asunto = '🎉 ¡Bienvenido a Selena Shop! Verifica tu email'
        resultado = enviar_email_directo(usuario.email, asunto, mensaje_html)
        return resultado
        
    except Exception as e:
        print(f"Error en enviar_email_verificacion: {e}")
        import traceback
        traceback.print_exc()
        return False


def login_usuario(request):
    """Vista de login para usuarios"""
    # Si el usuario ya está autenticado, redirigir según su rol
    if request.user.is_authenticated:
        if request.user.rol == 'admin_tienda' or request.user.is_staff:
            return redirect('core:admin_index')
        return redirect('usuarios:my_account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next')

        # Autenticar al usuario
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            
            # Si es admin_tienda o staff -> ir al panel admin
            if user.rol == 'admin_tienda' or user.is_staff:
                messages.success(request, f'Bienvenido al panel de administración, {user.email}')
                return redirect('core:admin_index')
            
            # Si es cliente -> ir a my account o a la página solicitada
            messages.success(request, f'¡Bienvenido de vuelta, {user.nombre or user.email}!')
            
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)
            
            return redirect('usuarios:my_account')
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
            return render(request, 'login.html', {'next': next_url})
    
    # GET request
    next_url = request.GET.get('next')
    return render(request, 'login.html', {'next': next_url})


def registrar_usuario(request):
    """Vista de registro para nuevos clientes"""
    # Si el usuario ya está autenticado, redirigir
    if request.user.is_authenticated:
        return redirect('usuarios:my_account')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        provincia_id = request.POST.get('provincia')
        ciudad_id = request.POST.get('ciudad')
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        # Validaciones
        if not email or not password:
            messages.error(request, 'El email y la contraseña son obligatorios.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'provincia_id': provincia_id,
                'ciudad_id': ciudad_id,
                'provincias': obtener_provincias(),
                'ciudades': obtener_ciudades_por_provincia(provincia_id) if provincia_id else []
            })
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'provincia_id': provincia_id,
                'ciudad_id': ciudad_id,
                'provincias': obtener_provincias(),
                'ciudades': obtener_ciudades_por_provincia(provincia_id) if provincia_id else []
            })
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'provincia_id': provincia_id,
                'ciudad_id': ciudad_id,
                'provincias': obtener_provincias(),
                'ciudades': obtener_ciudades_por_provincia(provincia_id) if provincia_id else []
            })
        
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'provincias': obtener_provincias(),
                'ciudades': obtener_ciudades_por_provincia(provincia_id) if provincia_id else []
            })
        
        try:
            # Obtener provincia y ciudad si fueron seleccionadas
            from .models import Provincia, Ciudad
            provincia = None
            ciudad = None
            
            if provincia_id:
                try:
                    provincia = Provincia.objects.get(id=provincia_id)
                except Provincia.DoesNotExist:
                    provincia = None
            
            if ciudad_id:
                try:
                    ciudad = Ciudad.objects.get(id=ciudad_id)
                except Ciudad.DoesNotExist:
                    ciudad = None
            
            # Crear el usuario con rol de cliente
            user = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                provincia=provincia,
                ciudad=ciudad,
                rol='cliente',  # Por defecto todos los registros desde la web son clientes
            )
            
            # Enviar email de verificación
            if enviar_email_verificacion(request, user):
                messages.success(
                    request, 
                    f'🎉 ¡Registro exitoso! Te hemos enviado un correo de bienvenida a {email}. '
                    'Revisa tu bandeja de entrada para verificar tu cuenta.'
                )
            else:
                messages.success(
                    request,
                    f'🎉 ¡Registro exitoso! Tu cuenta ha sido creada correctamente.'
                )
            
            # Autenticar y hacer login automáticamente (aunque el email no esté verificado)
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('usuarios:my_account')
            
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'provincia_id': provincia_id,
                'ciudad_id': ciudad_id,
                'provincias': obtener_provincias(),
                'ciudades': obtener_ciudades_por_provincia(provincia_id) if provincia_id else []
            })
    
    # GET request
    return render(request, 'register.html', {
        'provincias': obtener_provincias(),
        'ciudades': []
    })


def obtener_provincias():
    """Helper para obtener todas las provincias activas"""
    from .models import Provincia
    return Provincia.objects.filter(activa=True).order_by('nombre')


def obtener_ciudades_por_provincia(provincia_id):
    """Helper para obtener ciudades de una provincia específica"""
    from .models import Ciudad
    if provincia_id:
        try:
            return Ciudad.objects.filter(provincia_id=provincia_id, activa=True).order_by('nombre')
        except:
            return []
    return []


def logout_usuario(request):
    """Vista de logout para usuarios"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('usuarios:login')


@login_required(login_url='/')
def my_account(request):
    """Dashboard principal de la cuenta del usuario"""
    return render(request, 'my-account.html', {
        'user': request.user
    })


@login_required(login_url='/')
def my_account_orders(request):
    """Historial de órdenes del usuario"""
    # Obtener órdenes del usuario actual
    ordenes = request.user.pedidos.all().order_by('-created_at')
    
    # Paginar si hay muchas órdenes (10 por página)
    from django.core.paginator import Paginator
    paginator = Paginator(ordenes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'my-account-orders.html', {
        'user': request.user,
        'ordenes': page_obj,
    })


@login_required(login_url='/')
def my_account_orders_details(request, numero_pedido):
    """Detalles de una orden específica"""
    # Obtener la orden del usuario
    from django.shortcuts import get_object_or_404
    from core.models import Pedido
    
    orden = get_object_or_404(Pedido, numero_pedido=numero_pedido, usuario=request.user)
    
    return render(request, 'my-account-orders-details.html', {
        'user': request.user,
        'orden': orden,
    })


@login_required(login_url='/')
def my_account_address(request):
    """Gestión de direcciones del usuario"""
    # TODO: Obtener direcciones del usuario desde el modelo de Direcciones
    return render(request, 'my-account-address.html', {
        'user': request.user
    })


@login_required(login_url='/')
def my_account_edit(request):
    """Edición de detalles de la cuenta"""
    if request.method == 'POST':
        # TODO: Actualizar información del usuario
        messages.success(request, 'Información actualizada correctamente.')
        return redirect('usuarios:my_account_edit')
    
    return render(request, 'my-account-edit.html', {
        'user': request.user
    })


@login_required(login_url='/')
def my_account_wishlist(request):
    """Lista de deseos del usuario"""
    # TODO: Obtener productos favoritos del usuario
    return render(request, 'my-account-wishlist.html', {
        'user': request.user
    })


def password_reset_request(request):
    """Vista para solicitar restablecimiento de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Por favor ingresa tu email.')
            return redirect('usuarios:login')
        
        try:
            user = Usuario.objects.get(email=email)
            
            # Generar token de restablecimiento
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construir URL de restablecimiento
            reset_url = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            
            # Usar CID para el logo (Content-ID)
            logo_src = "cid:logoselena"
            
            # Crear email HTML profesional con logo y color de marca #918567
            nombre_usuario = user.nombre or user.email.split('@')[0]
            
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
                    .btn-container {{
                        text-align: center;
                        margin: 40px 0;
                    }}
                    .btn {{
                        display: inline-block;
                        background: linear-gradient(135deg, #918567 0%, #a89878 100%);
                        color: white !important;
                        padding: 18px 50px;
                        text-decoration: none;
                        border-radius: 50px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 8px 20px rgba(145, 133, 103, 0.3);
                        transition: all 0.3s ease;
                    }}
                    .btn:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 12px 24px rgba(145, 133, 103, 0.4);
                    }}
                    .divider {{
                        height: 1px;
                        background: linear-gradient(to right, transparent, #d4cfc4, transparent);
                        margin: 30px 0;
                    }}
                    .security-info {{
                        background: linear-gradient(to bottom, #faf9f7, #ffffff);
                        border: 2px solid #e8e3da;
                        border-left: 4px solid #918567;
                        padding: 20px;
                        margin: 30px 0;
                        border-radius: 8px;
                    }}
                    .security-info h3 {{
                        color: #918567;
                        margin: 0 0 10px;
                        font-size: 16px;
                    }}
                    .security-info p {{
                        margin: 5px 0;
                        color: #666;
                        font-size: 14px;
                    }}
                    .footer {{
                        background: linear-gradient(to bottom, #faf9f7, #f5f3f0);
                        padding: 30px;
                        text-align: center;
                        border-top: 2px solid #e8e3da;
                    }}
                    .footer-text {{
                        color: #999;
                        font-size: 13px;
                        margin: 5px 0;
                    }}
                    .footer-text a {{
                        color: #918567;
                        text-decoration: none;
                    }}
                    .link-alternative {{
                        margin-top: 20px;
                        padding: 15px;
                        background: #faf9f7;
                        border: 1px solid #e8e3da;
                        border-radius: 8px;
                        word-break: break-all;
                    }}
                    .link-alternative p {{
                        color: #888;
                        font-size: 12px;
                        margin: 0 0 10px;
                    }}
                    .link-alternative a {{
                        color: #918567;
                        font-size: 13px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <div class="logo-container">
                            <img src="{logo_src}" alt="Selena Shop" class="logo">
                        </div>
                        <h1 class="header-title">🔐 Restablecer Contraseña</h1>
                        <p class="header-subtitle">Solicitud de cambio de contraseña</p>
                    </div>
                    
                    <div class="content">
                        <p class="greeting">Hola <strong>{nombre_usuario}</strong>,</p>
                        
                        <p class="message">
                            Recibimos una solicitud para restablecer la contraseña de tu cuenta en <strong>Selena Shop</strong>. 
                            Si realizaste esta solicitud, haz clic en el botón de abajo para crear una nueva contraseña.
                        </p>
                        
                        <div class="btn-container">
                            <a href="{reset_url}" class="btn">
                                🔑 Restablecer mi Contraseña
                            </a>
                        </div>
                        
                        <div class="security-info">
                            <h3>🛡️ Información de Seguridad</h3>
                            <p>• Este enlace expira en <strong>24 horas</strong></p>
                            <p>• Solo funciona una vez</p>
                            <p>• Si no solicitaste este cambio, ignora este correo y tu contraseña permanecerá segura</p>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <div class="link-alternative">
                            <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                            <a href="{reset_url}">{reset_url}</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p class="footer-text">Este correo fue enviado automáticamente. Por favor no respondas.</p>
                        <p class="footer-text">© 2026 Selena Shop - Todos los derechos reservados</p>
                        <p class="footer-text" style="margin-top: 15px;">
                            ¿No solicitaste este cambio? <a href="mailto:soporte@selenashop.com">Contáctanos</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar correo usando la función personalizada
            asunto = '🔐 Restablece tu contraseña - Selena Shop'
            
            if enviar_email_directo(user.email, asunto, mensaje_html):
                messages.success(
                    request, 
                    '✅ Se ha enviado un correo con las instrucciones para restablecer tu contraseña. '
                    'Revisa tu bandeja de entrada.'
                )
            else:
                messages.error(
                    request, 
                    '❌ Hubo un problema al enviar el correo. Por favor intenta nuevamente.'
                )
                
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            messages.success(
                request, 
                '✅ Si el email existe en nuestro sistema, recibirás un correo con las instrucciones.'
            )
        
        return redirect('usuarios:login')
    
    return redirect('usuarios:login')
    """Vista para solicitar restablecimiento de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Por favor ingresa tu email.')
            return redirect('usuarios:login')
        
        try:
            user = Usuario.objects.get(email=email)
            
            # Generar token de restablecimiento
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construir URL de restablecimiento
            reset_url = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            
            # Crear email HTML profesional con logo
            nombre_usuario = user.nombre or user.email.split('@')[0]
            
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
                        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 50px 30px;
                        text-align: center;
                    }}
                    .logo {{
                        width: 120px;
                        height: auto;
                        margin-bottom: 20px;
                        background: white;
                        padding: 10px;
                        border-radius: 10px;
                    }}
                    .header-title {{
                        color: white;
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .header-subtitle {{
                        color: rgba(255,255,255,0.9);
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
                    .btn-container {{
                        text-align: center;
                        margin: 40px 0;
                    }}
                    .btn {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white !important;
                        padding: 18px 50px;
                        text-decoration: none;
                        border-radius: 50px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
                        transition: transform 0.3s;
                    }}
                    .btn:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.4);
                    }}
                    .divider {{
                        height: 1px;
                        background: linear-gradient(to right, transparent, #e0e0e0, transparent);
                        margin: 30px 0;
                    }}
                    .security-info {{
                        background: #f8f9ff;
                        border-left: 4px solid #667eea;
                        padding: 20px;
                        margin: 30px 0;
                        border-radius: 8px;
                    }}
                    .security-info h3 {{
                        color: #667eea;
                        margin: 0 0 10px;
                        font-size: 16px;
                    }}
                    .security-info p {{
                        margin: 5px 0;
                        color: #666;
                        font-size: 14px;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #eee;
                    }}
                    .footer-text {{
                        color: #999;
                        font-size: 13px;
                        margin: 5px 0;
                    }}
                    .link-alternative {{
                        margin-top: 20px;
                        padding: 15px;
                        background: #f5f5f5;
                        border-radius: 8px;
                        word-break: break-all;
                    }}
                    .link-alternative p {{
                        color: #888;
                        font-size: 12px;
                        margin: 0 0 10px;
                    }}
                    .link-alternative a {{
                        color: #667eea;
                        font-size: 13px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <div style="text-align: center;">
                            <div style="background: white; display: inline-block; padding: 15px 25px; border-radius: 12px;">
                                <h1 style="margin: 0; color: #667eea; font-size: 32px; font-weight: 800;">Selena Shop</h1>
                            </div>
                        </div>
                        <h1 class="header-title">🔐 Restablecer Contraseña</h1>
                        <p class="header-subtitle">Solicitud de cambio de contraseña</p>
                    </div>
                    
                    <div class="content">
                        <p class="greeting">Hola <strong>{nombre_usuario}</strong>,</p>
                        
                        <p class="message">
                            Recibimos una solicitud para restablecer la contraseña de tu cuenta en Selena Shop. 
                            Si realizaste esta solicitud, haz clic en el botón de abajo para crear una nueva contraseña.
                        </p>
                        
                        <div class="btn-container">
                            <a href="{reset_url}" class="btn">
                                🔑 Restablecer mi Contraseña
                            </a>
                        </div>
                        
                        <div class="security-info">
                            <h3>🛡️ Información de Seguridad</h3>
                            <p>• Este enlace expira en <strong>24 horas</strong></p>
                            <p>• Solo funciona una vez</p>
                            <p>• Si no solicitaste este cambio, ignora este correo</p>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <div class="link-alternative">
                            <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                            <a href="{reset_url}">{reset_url}</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p class="footer-text">Este correo fue enviado automáticamente. Por favor no respondas.</p>
                        <p class="footer-text">© 2026 Selena Shop - Todos los derechos reservados</p>
                        <p class="footer-text" style="margin-top: 15px;">
                            ¿No solicitaste este cambio? <a href="mailto:soporte@selenashop.com" style="color: #667eea;">Contáctanos</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar correo usando la función personalizada
            asunto = '🔐 Restablece tu contraseña - Selena Shop'
            
            if enviar_email_directo(user.email, asunto, mensaje_html):
                messages.success(
                    request, 
                    '✅ Se ha enviado un correo con las instrucciones para restablecer tu contraseña. '
                    'Revisa tu bandeja de entrada.'
                )
            else:
                messages.error(
                    request, 
                    '❌ Hubo un problema al enviar el correo. Por favor intenta nuevamente.'
                )
                
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            messages.success(
                request, 
                '✅ Si el email existe en nuestro sistema, recibirás un correo con las instrucciones.'
            )
        
        return redirect('usuarios:login')
    
    return redirect('usuarios:login')


def password_reset_confirm(request, uidb64, token):
    """Vista para confirmar y establecer nueva contraseña"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password', '').strip()
            password_confirm = request.POST.get('password_confirm', '').strip()
            
            if not password:
                messages.error(request, 'La contraseña es obligatoria.')
                return render(request, 'password_reset_confirm.html', {
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
            
            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'password_reset_confirm.html', {
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
            
            if len(password) < 6:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return render(request, 'password_reset_confirm.html', {
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
            
            # Establecer la nueva contraseña
            user.set_password(password)
            user.save()
            
            messages.success(request, '¡Tu contraseña ha sido restablecida exitosamente! Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
        
        # GET request - mostrar formulario
        return render(request, 'password_reset_confirm.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        # Token inválido o expirado
        messages.error(request, 'El enlace de restablecimiento es inválido o ha expirado.')
        return redirect('usuarios:login')


# ==================== API AJAX ====================

def api_ciudades_por_provincia(request, provincia_id):
    """API para obtener ciudades por provincia (AJAX)"""
    from .models import Ciudad
    
    try:
        ciudades = Ciudad.objects.filter(
            provincia_id=provincia_id,
            activa=True
        ).values('id', 'nombre').order_by('nombre')
        
        return JsonResponse({
            'success': True,
            'ciudades': list(ciudades)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ==================== VERIFICACIÓN DE EMAIL ====================

def verificar_email(request, token):
    """Vista para verificar el email del usuario"""
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        
        if not token_obj.es_valido():
            messages.error(
                request, 
                '⏰ El enlace de verificación ha expirado o ya fue utilizado. '
                'Por favor solicita un nuevo correo de verificación.'
            )
            return redirect('usuarios:login')
        
        # Marcar el email como verificado
        usuario = token_obj.usuario
        
        # Marcar el token como usado
        token_obj.usado = True
        token_obj.save()
        
        messages.success(
            request, 
            '✅ ¡Tu email ha sido verificado exitosamente! Ya puedes disfrutar de todas las funciones de Selena Shop.'
        )
        
        # Mostrar página de verificación exitosa
        return render(request, 'email_verificado.html', {
            'usuario': usuario
        })
        
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, '❌ El enlace de verificación no es válido o ha expirado.')
        return redirect('usuarios:login')


@login_required(login_url='/')
def reenviar_verificacion(request):
    """Vista para reenviar el correo de verificación"""
    usuario = request.user
    
    # El campo email_verificado no existe en el modelo
    # if usuario.email_verificado:
    #     messages.info(request, 'Tu email ya está verificado.')
    #     return redirect('usuarios:my_account')
    
    # Invalidar tokens anteriores
    EmailVerificationToken.objects.filter(usuario=usuario, usado=False).update(usado=True)
    
    # Enviar nuevo correo
    if enviar_email_verificacion(request, usuario):
        messages.success(
            request, 
            f'Hemos enviado un nuevo correo de verificación a {usuario.email}. '
            'Por favor revisa tu bandeja de entrada (y spam).'
        )
    else:
        messages.error(
            request,
            'Hubo un problema al enviar el correo. Por favor intenta más tarde.'
        )
    
    return redirect('usuarios:my_account')


# ==================== WISHLIST ====================
@login_required(login_url='usuarios:login')
def my_account_wishlist(request):
    """
    Vista para mostrar la lista de deseos del usuario
    """
    from .models import Wishlist
    
    wishlist_items = Wishlist.objects.filter(usuario=request.user).select_related('producto')
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_items.count()
    }
    
    return render(request, 'wishlist.html', context)


@login_required(login_url='usuarios:login')
def add_to_wishlist(request, producto_id):
    """
    Vista AJAX para agregar producto a la lista de deseos
    """
    from apps.productos.models import Producto
    from .models import Wishlist
    
    try:
        producto = Producto.objects.get(id=producto_id)
        
        # Verificar si ya está en el wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            usuario=request.user,
            producto=producto
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': f'{producto.nombre} agregado a tu lista de deseos',
                'action': 'added'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f'{producto.nombre} ya estaba en tu lista de deseos',
                'action': 'already_exists'
            })
    
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@login_required(login_url='usuarios:login')
def remove_from_wishlist(request, wishlist_id):
    """
    Vista AJAX para eliminar producto de la lista de deseos
    """
    from .models import Wishlist
    
    try:
        wishlist_item = Wishlist.objects.get(id=wishlist_id, usuario=request.user)
        producto_nombre = wishlist_item.producto.nombre
        wishlist_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{producto_nombre} eliminado de tu lista de deseos'
        })
    
    except Wishlist.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado en tu wishlist'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def is_in_wishlist(request, producto_id):
    """
    Vista AJAX para verificar si un producto está en el wishlist
    """
    if not request.user.is_authenticated:
        return JsonResponse({'in_wishlist': False})
    
    from apps.productos.models import Producto
    from .models import Wishlist
    
    try:
        in_wishlist = Wishlist.objects.filter(
            usuario=request.user,
            producto_id=producto_id
        ).exists()
        
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
