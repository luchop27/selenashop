from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class AdminAccessMiddleware:
    """
    Middleware que protege todas las rutas del panel de administración.
    Solo usuarios con is_staff=True o is_superuser=True pueden acceder.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Lista de rutas administrativas a proteger
        admin_paths = [
            '/admin/productos/',
            '/admin/categorias/',
            '/admin/colecciones/',
            '/admin/atributos/',
            '/admin/ordenes/',
            '/admin/usuarios/',
            '/admin/dashboard/',
            '/admin/panel/',
            '/admin-ecomus/',
        ]
        
        # Rutas públicas permitidas (login del admin)
        public_admin_paths = [
            '/admin/login/',
            '/admin/logout/',
        ]
        
        # Verificar si la ruta actual es administrativa
        path = request.path
        is_admin_route = any(path.startswith(admin_path) for admin_path in admin_paths)
        is_public_admin = any(path.startswith(public_path) for public_path in public_admin_paths)
        
        # Si es una ruta administrativa y no es pública
        if is_admin_route and not is_public_admin:
            # Verificar autenticación
            if not request.user.is_authenticated:
                messages.warning(request, 'Debes iniciar sesión para acceder al panel de administración.')
                return redirect('/admin/login/')
            
            # Verificar permisos de administrador
            if not (request.user.is_staff or request.user.is_superuser):
                messages.error(request, 'No tienes permisos para acceder al panel de administración.')
                return redirect('core:inicio')
        
        response = self.get_response(request)
        return response
