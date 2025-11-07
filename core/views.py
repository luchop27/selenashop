from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def inicio(request):
    """Renderiza la plantilla home-05.html (nuevo index)"""
    return render(request, 'home-05.html')


def home_05(request):
    """Alias para la función inicio"""
    return inicio(request)

def shop_collection_sub(request):
    # Aquí va la lógica de la vista
    return render(request, 'shop-collection-sub.html')


# Alias para las vistas de usuarios (para mantener compatibilidad)
def login_usuario(request):
    """Alias a la vista de login en usuarios"""
    from apps.usuarios.views import login_usuario as login_view
    return login_view(request)


def logout_usuario(request):
    """Alias a la vista de logout en usuarios"""
    from apps.usuarios.views import logout_usuario as logout_view
    return logout_view(request)


@login_required(login_url='/login/')
def dashboard_redirect(request):
    """Redirección al dashboard si el usuario es admin"""
    if request.user.rol == 'admin_tienda' or request.user.is_staff:
        return redirect('core:admin_index')
    else:
        messages.error(request, 'No tienes permiso para acceder al panel de administración.')
        return redirect('core:inicio')


def admin_index(request):
    """Renderiza el índice del panel administrativo"""
    if not request.user.is_authenticated or (request.user.rol != 'admin_tienda' and not request.user.is_staff):
        return redirect('core:inicio')
    # Render the original admin HTML (pindex.html) which is located in the
    # project folder `admin-ecomus/` and is included in TEMPLATES['DIRS'].
    return render(request, 'pindex.html')