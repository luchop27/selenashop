from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorador para vistas que requieren permisos de administrador.
    Solo usuarios staff o superuser pueden acceder.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Primero verificar si está autenticado
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder al panel de administración.')
            return redirect('/admin/login/')
        
        # Verificar si es staff o superuser
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para acceder al panel de administración.')
            return redirect('core:inicio')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def superuser_required(view_func):
    """
    Decorador para vistas que requieren permisos de superusuario.
    Solo superusers pueden acceder.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Primero verificar si está autenticado
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión.')
            return redirect('/admin/login/')
        
        # Verificar si es superuser
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos suficientes para realizar esta acción.')
            return redirect('core:inicio')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
