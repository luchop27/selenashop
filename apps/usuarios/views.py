from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme


def login_usuario(request):
    """Vista de login para usuarios"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Obtener posible URL de retorno (prioriza campo `next`) o referer
        next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER')

        print(f"DEBUG: Intentando autenticar con email: {email}")

        # Autenticar al usuario
        user = authenticate(request, username=email, password=password)

        print(f"DEBUG: Usuario autenticado: {user}")
        if user is not None:
            print(f"DEBUG: Rol del usuario: {getattr(user, 'rol', None)}, is_staff: {user.is_staff}")

        if user is not None:
            # Si es admin_tienda o staff -> ir al panel admin
            if getattr(user, 'rol', None) == 'admin_tienda' or user.is_staff:
                login(request, user)
                print(f"DEBUG: Usuario {email} autenticado y redirigido al panel admin")
                # Redirigir al panel de administración
                return redirect('core:admin_index')

            # Si es cliente u otro usuario autenticado -> volver a la página de origen si es segura
            login(request, user)
            # Validar que next_url pertenezca al mismo host y no apunte al login/otra acción
            if next_url:
                try:
                    allowed = url_has_allowed_host_and_scheme(next_url, {request.get_host()})
                except Exception:
                    allowed = False
                # Evitar redirigir de vuelta a la página de login o logout
                if allowed and ('login' not in next_url and 'logout' not in next_url):
                    print(f"DEBUG: Redirigiendo cliente a: {next_url}")
                    return redirect(next_url)

            # Por defecto, quedarse en la página principal
            print(f"DEBUG: Redirigiendo cliente a inicio")
            return redirect('inicio')
        else:
            print(f"DEBUG: Autenticación fallida para {email}")
            messages.error(request, 'Email o contraseña incorrectos.')
            # Intentar volver a la página de origen si existe
            if request.META.get('HTTP_REFERER'):
                return redirect(request.META.get('HTTP_REFERER'))
            return redirect('inicio')
    
    return redirect('inicio')


def logout_usuario(request):
    """Vista de logout para usuarios"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('core:inicio')


@login_required(login_url='/')
def my_account(request):
    """Renderiza la plantilla my-account.html"""
    # El archivo my-account.html está en htmls/
    return render(request, '../htmls/my-account.html')
