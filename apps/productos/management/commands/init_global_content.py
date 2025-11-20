from django.core.management.base import BaseCommand
from apps.productos.models import GlobalProductContent


class Command(BaseCommand):
    help = 'Inicializa GlobalProductContent con valores por defecto'

    def handle(self, *args, **options):
        if GlobalProductContent.objects.exists():
            self.stdout.write(self.style.WARNING('GlobalProductContent ya existe. No se creará otra instancia.'))
            return
        
        # Contenido HTML por defecto para Features
        features_html = """<li>Front button placket</li>
                    <li>Adjustable sleeve button</li>
                    <li>Double chest pockets</li>
                    <li>Button lined</li>
                    <li>Product Type: Shirt</li>"""
        
        # Contenido HTML por defecto para Materials
        materials_html = """<li>Content: 100% Cotton</li>
                    <li>Weight: 200 GSM</li>
                    <li>Dimensions: 10 x 10 x 15 cm</li>"""
        
        global_content = GlobalProductContent.objects.create(
            features_content=features_html,
            materials_content=materials_html,
            care_icon_1="icon-machine",
            care_text_1="Machine wash max. 30ºC. Short spin.",
            care_icon_2="icon-iron",
            care_text_2="Iron maximum 110ºC.",
            care_icon_3="icon-bleach",
            care_text_3="Do not bleach/bleach.",
            care_icon_4="icon-dry-clean",
            care_text_4="Do not dry clean.",
            care_icon_5="icon-tumble-dry",
            care_text_5="Tumble dry, medium hear.",
            product_code_text="LT01: 70% wool, 15% polyester, 10% polyamide, 5% acrylic 900 Grms/mt",
            activo=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'GlobalProductContent creado exitosamente: {global_content}'))
