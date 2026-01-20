from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.productos'
    
    def ready(self):
        """Importar señales cuando la app esté lista"""
        import apps.productos.signals
