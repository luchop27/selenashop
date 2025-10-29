from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def inicio(request):
    """Renderiza la plantilla inicio.html"""
    return render(request, 'index.html')


def home_02(request):
    """Renderiza la plantilla home-02.html"""
    return render(request, 'home-02.html')


def login_usuario(request):
    """Vista de login para usuarios"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"DEBUG: Intentando autenticar con email: {email}")
        
        # Autenticar al usuario
        user = authenticate(request, username=email, password=password)
        
        print(f"DEBUG: Usuario autenticado: {user}")
        if user is not None:
            print(f"DEBUG: Rol del usuario: {user.rol}, is_staff: {user.is_staff}")
        
        if user is not None:
            # Verificar si es admin_tienda
            if user.rol == 'admin_tienda' or user.is_staff:
                login(request, user)
                print(f"DEBUG: Usuario {email} autenticado y redirigido a admin_index")
                # Redirigir al panel admin
                return redirect('admin_index')
            else:
                print(f"DEBUG: Usuario no es admin_tienda. Rol: {user.rol}")
                messages.error(request, 'No tienes permiso para acceder al panel de administración.')
                return redirect('home_02')
        else:
            print(f"DEBUG: Autenticación fallida para {email}")
            messages.error(request, 'Email o contraseña incorrectos.')
            return redirect('home_02')
    
    return redirect('home_02')


def admin_index(request):
    """Renderiza el índice del panel administrativo"""
    if not request.user.is_authenticated or (request.user.rol != 'admin_tienda' and not request.user.is_staff):
        return redirect('home_02')
    return render(request, 'pindex.html')


def logout_usuario(request):
    """Vista de logout para usuarios"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('inicio')


@login_required(login_url='home_02')
def dashboard_redirect(request):
    """Redirección al dashboard si el usuario es admin"""
    if request.user.rol == 'admin_tienda' or request.user.is_staff:
        return redirect('productos:dashboard')
    else:
        messages.error(request, 'No tienes permiso para acceder al panel de administración.')
        return redirect('inicio')

