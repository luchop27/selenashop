from django.core.management.base import BaseCommand
from apps.productos.models import Producto, Variante, Talla


class Command(BaseCommand):
    help = 'Corrige las variantes asignándoles tallas según el SKU'

    def handle(self, *args, **options):
        # Asegurarse de que existen las tallas básicas
        tallas_basicas = ['S', 'M', 'L', 'XL', 'XS', 'XXL']
        for codigo in tallas_basicas:
            talla, created = Talla.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': codigo}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Talla {codigo} creada'))
        
        # Obtener el producto Veraniegos
        try:
            producto = Producto.objects.get(id=24)
            self.stdout.write(f'Producto encontrado: {producto.nombre}')
            
            # Obtener sus variantes
            variantes = producto.variantes.all()
            self.stdout.write(f'Variantes encontradas: {variantes.count()}')
            
            # Asignar tallas según el SKU o el orden
            tallas_a_asignar = ['S', 'M', 'L']
            
            for idx, variante in enumerate(variantes):
                if variante.talla is None and idx < len(tallas_a_asignar):
                    codigo_talla = tallas_a_asignar[idx]
                    talla = Talla.objects.get(codigo=codigo_talla)
                    variante.talla = talla
                    variante.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Variante ID {variante.id} (SKU: {variante.sku}) -> Talla {codigo_talla} asignada'
                        )
                    )
                elif variante.talla:
                    self.stdout.write(f'Variante ID {variante.id} ya tiene talla: {variante.talla.codigo}')
            
            self.stdout.write(self.style.SUCCESS('¡Corrección completada!'))
            
        except Producto.DoesNotExist:
            self.stdout.write(self.style.ERROR('Producto con ID 24 no encontrado'))
