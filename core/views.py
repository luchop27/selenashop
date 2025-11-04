from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def inicio(request):
    """Renderiza la plantilla home-05.html (nuevo index)"""
    return render(request, 'home-05.html')


def home_05(request):
    """Alias para la función inicio"""
    return inicio(request)


@login_required(login_url='usuarios:login')
def dashboard_redirect(request):
    """Redirección al dashboard si el usuario es admin"""
    if request.user.rol == 'admin_tienda' or request.user.is_staff:
        return redirect('admin_index')
    else:
        messages.error(request, 'No tienes permiso para acceder al panel de administración.')
        return redirect('inicio')


def admin_index(request):
    """Renderiza el índice del panel administrativo"""
    if not request.user.is_authenticated or (request.user.rol != 'admin_tienda' and not request.user.is_staff):
        return redirect('inicio')
    # Render the original admin HTML (pindex.html) which is located in the
    # project folder `admin-ecomus/` and is included in TEMPLATES['DIRS'].
    return render(request, 'pindex.html')