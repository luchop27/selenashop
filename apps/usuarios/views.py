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
from .models import Usuario


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
                rol='cliente'  # Por defecto todos los registros desde la web son clientes
            )
            
            # Autenticar y hacer login automáticamente
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'¡Bienvenido {nombre}! Tu cuenta ha sido creada exitosamente.')
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
    # TODO: Obtener órdenes del usuario desde el modelo de Pedidos
    return render(request, 'my-account-orders.html', {
        'user': request.user
    })


@login_required(login_url='/')
def my_account_orders_details(request, order_id):
    """Detalles de una orden específica"""
    # TODO: Obtener detalles de la orden desde el modelo de Pedidos
    return render(request, 'my-account-orders-details.html', {
        'user': request.user,
        'order_id': order_id
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
                f'/usuarios/password-reset-confirm/{uid}/{token}/'
            )
            
            # Preparar el correo
            subject = 'Restablecimiento de contraseña - Selena Shop'
            message = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'domain': request.get_host(),
            })
            
            # Enviar correo
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=message,
                    fail_silently=False,
                )
                messages.success(request, 'Se ha enviado un correo con las instrucciones para restablecer tu contraseña.')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {str(e)}')
                
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            messages.success(request, 'Si el email existe en nuestro sistema, recibirás un correo con las instrucciones.')
        
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

