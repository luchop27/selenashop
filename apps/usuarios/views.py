from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
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
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        # Validaciones
        if not email or not password:
            messages.error(request, 'El email y la contraseña son obligatorios.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email
            })
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email
            })
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email
            })
        
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado.')
            return render(request, 'register.html', {
                'nombre': nombre,
                'apellido': apellido
            })
        
        try:
            # Crear el usuario con rol de cliente
            user = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
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
                'email': email
            })
    
    # GET request
    return render(request, 'register.html')


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
