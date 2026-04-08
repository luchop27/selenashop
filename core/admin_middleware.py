from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.urls import reverse


class AdminAccessMiddleware:
    """
    Middleware que protege todas las rutas del panel de administración.
    Solo usuarios con is_staff=True o is_superuser=True pueden acceder.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.storefront_message_fragments = (
            'tu carrito está vacío',
            'tu carrito esta vacio',
            'tu carrito estã¡ vacã­o',
            'agrega productos antes de continuar',
        )
        self.admin_message_fragments = (
            'eliminado exitosamente',
            'eliminada exitosamente',
            'actualizado exitosamente',
            'actualizada exitosamente',
            'agregado exitosamente',
            'agregada exitosamente',
            'editado exitosamente',
            'editada exitosamente',
            'marcado como pagado',
            'cancelado y stock devuelto',
            'panel de administración',
            'panel de administracion',
            'no tienes permisos para acceder al panel',
        )

    def _clear_pending_messages(self, request):
        """Consume todos los mensajes pendientes del storage actual."""
        storage = get_messages(request)
        storage.used = True

    def _is_storefront_message(self, message):
        tags = (message.tags or '').lower()
        text = str(message).strip().lower()

        if 'storefront' in tags:
            return True

        return any(fragment in text for fragment in self.storefront_message_fragments)

    def _is_admin_message(self, message):
        tags = (message.tags or '').lower()
        text = str(message).strip().lower()

        if 'admin' in tags:
            return True

        return any(fragment in text for fragment in self.admin_message_fragments)

    def _strip_storefront_messages_for_admin(self, request):
        """Consume y vuelve a cargar solo mensajes válidos para admin."""
        storage = get_messages(request)
        kept_messages = []

        for message in storage:
            if self._is_storefront_message(message):
                continue
            kept_messages.append((message.level, str(message), message.extra_tags))

        for level, text, extra_tags in kept_messages:
            messages.add_message(request, level, text, extra_tags=extra_tags)

    def _strip_admin_messages_for_storefront(self, request):
        """Consume y vuelve a cargar solo mensajes válidos para storefront."""
        storage = get_messages(request)
        kept_messages = []

        for message in storage:
            if self._is_admin_message(message):
                continue
            kept_messages.append((message.level, str(message), message.extra_tags))

        for level, text, extra_tags in kept_messages:
            messages.add_message(request, level, text, extra_tags=extra_tags)
        
    def __call__(self, request):
        # Lista de rutas administrativas a proteger
        admin_paths = [
            '/admin/',
            '/admin-panel/',
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

        # Evitar que mensajes del storefront (carrito/checkout) se muestren en admin.
        if is_admin_route:
            request.session['last_admin_route'] = True
            self._strip_storefront_messages_for_admin(request)
        else:
            # Si la request previa fue administrativa, limpiar completamente la cola pendiente.
            if request.session.pop('last_admin_route', False):
                self._clear_pending_messages(request)

            # Defensa adicional: nunca mostrar mensajes administrativos en storefront.
            self._strip_admin_messages_for_storefront(request)
        
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
