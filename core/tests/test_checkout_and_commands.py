from datetime import timedelta
from decimal import Decimal
import threading
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.db import close_old_connections, connection
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from apps.productos.models import Producto, Variante
from core.models import DetallePedido, Pedido


class CheckoutProcessTests(TestCase):
    def setUp(self):
        self.checkout_url = reverse('core:checkout_process')

    def _crear_producto_variante(self, stock=5, precio='25.00'):
        producto = Producto.objects.create(
            nombre='Producto Test',
            slug=f'producto-test-{Producto.objects.count() + 1}',
            precio_base=Decimal(precio),
            activo=True,
        )
        variante = Variante.objects.create(
            producto=producto,
            sku=f'SKU-{producto.id}-{Variante.objects.count() + 1}',
            precio=Decimal(precio),
            stock=stock,
        )
        return producto, variante

    def _guardar_carrito_sesion(self, lineas):
        session = self.client.session
        session[settings.CART_SESSION_ID] = lineas
        session.save()

    def _post_checkout(self):
        return self.client.post(
            self.checkout_url,
            {
                'first_name': 'Marco',
                'last_name': 'Tester',
                'email': 'cliente@test.com',
                'phone': '0999999999',
                'country': 'Ecuador',
                'city': 'Machala',
                'address': 'Av. Principal 123',
                'shipping_cost': '0',
            },
        )

    def test_checkout_exitoso_descuenta_stock_y_crea_pedido(self):
        producto, variante = self._crear_producto_variante(stock=5, precio='25.00')
        self._guardar_carrito_sesion(
            {
                f'{producto.id}_{variante.id}': {
                    'producto_id': producto.id,
                    'producto_slug': producto.slug,
                    'variante_id': variante.id,
                    'nombre': producto.nombre,
                    'precio': '25.00',
                    'quantity': 2,
                    'imagen': '',
                    'color': None,
                    'talla': None,
                    'talla_nombre': None,
                }
            }
        )

        response = self._post_checkout()

        self.assertEqual(response.status_code, 302)
        self.assertIn('/pedido/confirmacion/', response.url)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(DetallePedido.objects.count(), 1)

        variante.refresh_from_db()
        self.assertEqual(variante.stock, 3)

        session = self.client.session
        self.assertEqual(session.get(settings.CART_SESSION_ID), {})

    def test_checkout_stock_insuficiente_no_crea_pedido(self):
        producto, variante = self._crear_producto_variante(stock=1, precio='19.00')
        self._guardar_carrito_sesion(
            {
                f'{producto.id}_{variante.id}': {
                    'producto_id': producto.id,
                    'producto_slug': producto.slug,
                    'variante_id': variante.id,
                    'nombre': producto.nombre,
                    'precio': '19.00',
                    'quantity': 2,
                    'imagen': '',
                    'color': None,
                    'talla': None,
                    'talla_nombre': None,
                }
            }
        )

        response = self._post_checkout()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:checkout'))
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(DetallePedido.objects.count(), 0)

        variante.refresh_from_db()
        self.assertEqual(variante.stock, 1)

    def test_checkout_falla_whatsapp_no_bloquea_pedido(self):
        producto, variante = self._crear_producto_variante(stock=4, precio='30.00')
        self._guardar_carrito_sesion(
            {
                f'{producto.id}_{variante.id}': {
                    'producto_id': producto.id,
                    'producto_slug': producto.slug,
                    'variante_id': variante.id,
                    'nombre': producto.nombre,
                    'precio': '30.00',
                    'quantity': 1,
                    'imagen': '',
                    'color': None,
                    'talla': None,
                    'talla_nombre': None,
                }
            }
        )

        with patch('core.whatsapp_utils.enviar_notificacion_pedido', side_effect=Exception('fallo whatsapp')):
            response = self._post_checkout()

        self.assertEqual(response.status_code, 302)
        self.assertIn('/pedido/confirmacion/', response.url)
        self.assertEqual(Pedido.objects.count(), 1)

        variante.refresh_from_db()
        self.assertEqual(variante.stock, 3)

    def test_checkout_agrega_cantidades_si_variante_esta_repetida_en_carrito(self):
        producto, variante = self._crear_producto_variante(stock=3, precio='10.00')
        self._guardar_carrito_sesion(
            {
                'linea_1': {
                    'producto_id': producto.id,
                    'producto_slug': producto.slug,
                    'variante_id': variante.id,
                    'nombre': producto.nombre,
                    'precio': '10.00',
                    'quantity': 2,
                    'imagen': '',
                    'color': None,
                    'talla': None,
                    'talla_nombre': None,
                },
                'linea_2': {
                    'producto_id': producto.id,
                    'producto_slug': producto.slug,
                    'variante_id': variante.id,
                    'nombre': producto.nombre,
                    'precio': '10.00',
                    'quantity': 2,
                    'imagen': '',
                    'color': None,
                    'talla': None,
                    'talla_nombre': None,
                },
            }
        )

        response = self._post_checkout()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:checkout'))
        self.assertEqual(Pedido.objects.count(), 0)

        variante.refresh_from_db()
        self.assertEqual(variante.stock, 3)


class CheckoutConcurrencyTransactionTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.checkout_url = reverse('core:checkout_process')
        self.payload = {
            'first_name': 'Cliente',
            'last_name': 'Concurrente',
            'email': 'cliente.concurrente@test.com',
            'phone': '0999999999',
            'country': 'Ecuador',
            'city': 'Machala',
            'address': 'Av. Principal 100',
            'shipping_cost': '0',
        }

        # bajo_pedido=True evita señales que eliminan productos al llegar stock a 0.
        self.producto = Producto.objects.create(
            nombre='Producto Concurrencia',
            slug=f'producto-concurrencia-{Producto.objects.count() + 1}',
            precio_base=Decimal('20.00'),
            activo=True,
            bajo_pedido=True,
        )
        self.variante = Variante.objects.create(
            producto=self.producto,
            sku=f'SKU-CONCURRENCIA-{Variante.objects.count() + 1}',
            precio=Decimal('20.00'),
            stock=1,
        )

    def _linea_carrito(self):
        return {
            f'{self.producto.id}_{self.variante.id}': {
                'producto_id': self.producto.id,
                'producto_slug': self.producto.slug,
                'variante_id': self.variante.id,
                'nombre': self.producto.nombre,
                'precio': '20.00',
                'quantity': 1,
                'imagen': '',
                'color': None,
                'talla': None,
                'talla_nombre': None,
            }
        }

    def _crear_cliente_con_carrito(self):
        client = Client()
        session = client.session
        session[settings.CART_SESSION_ID] = self._linea_carrito()
        session.save()
        return client

    def _worker_checkout(self, start_event, resultados, idx):
        close_old_connections()
        try:
            client = self._crear_cliente_con_carrito()
            if not start_event.wait(timeout=10):
                raise RuntimeError('Timeout esperando inicio concurrente')
            response = client.post(self.checkout_url, self.payload)
            resultados[idx] = {
                'status': response.status_code,
                'url': response.url,
            }
        except Exception as exc:
            resultados[idx] = {'error': repr(exc)}
        finally:
            close_old_connections()

    def test_checkout_concurrente_misma_variante_solo_una_compra_gana(self):
        if not connection.features.has_select_for_update:
            self.skipTest('El backend actual no soporta select_for_update para prueba de concurrencia real.')

        start_event = threading.Event()
        resultados = {}
        threads = [
            threading.Thread(target=self._worker_checkout, args=(start_event, resultados, 1), daemon=True),
            threading.Thread(target=self._worker_checkout, args=(start_event, resultados, 2), daemon=True),
        ]

        with patch('core.whatsapp_utils.enviar_notificacion_pedido', return_value={'success': True}):
            for thread in threads:
                thread.start()

            start_event.set()

            for thread in threads:
                thread.join(timeout=20)

        for thread in threads:
            self.assertFalse(thread.is_alive(), 'Una hebra de checkout quedó bloqueada.')

        self.assertEqual(len(resultados), 2)
        self.assertNotIn('error', resultados[1])
        self.assertNotIn('error', resultados[2])

        urls = [resultados[1]['url'], resultados[2]['url']]
        exitosos = [url for url in urls if '/pedido/confirmacion/' in url]
        fallidos = [url for url in urls if url == reverse('core:checkout')]

        self.assertEqual(len(exitosos), 1)
        self.assertEqual(len(fallidos), 1)

        self.variante.refresh_from_db()
        self.assertEqual(self.variante.stock, 0)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(DetallePedido.objects.count(), 1)


class CancelUnpaidOrdersCommandTests(TestCase):
    def _crear_producto_variante(self, stock=10):
        producto = Producto.objects.create(
            nombre=f'Producto cmd {Producto.objects.count() + 1}',
            slug=f'producto-cmd-{Producto.objects.count() + 1}',
            precio_base=Decimal('15.00'),
            activo=True,
            bajo_pedido=True,
        )
        variante = Variante.objects.create(
            producto=producto,
            sku=f'SKU-CMD-{producto.id}-{Variante.objects.count() + 1}',
            precio=Decimal('15.00'),
            stock=stock,
        )
        return producto, variante

    def _crear_pedido(self, *, estado='pendiente', pagado=False, metodo='bank_transfer', horas=3):
        pedido = Pedido.objects.create(
            email='cliente@test.com',
            first_name='Cliente',
            last_name='Test',
            phone='0999999999',
            country='Ecuador',
            city='Machala',
            address='Direccion 123',
            metodo_pago=metodo,
            subtotal=Decimal('30.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('30.00'),
            estado=estado,
            pagado=pagado,
        )
        Pedido.objects.filter(id=pedido.id).update(
            created_at=timezone.now() - timedelta(hours=horas),
            updated_at=timezone.now() - timedelta(hours=horas),
        )
        pedido.refresh_from_db()
        return pedido

    def test_cancel_unpaid_orders_cancela_vencidos_y_restaura_stock(self):
        producto, variante = self._crear_producto_variante(stock=3)

        pedido_objetivo = self._crear_pedido(estado='pendiente', pagado=False, metodo='bank_transfer', horas=3)
        DetallePedido.objects.create(
            pedido=pedido_objetivo,
            producto=producto,
            variante=variante,
            nombre_producto=producto.nombre,
            precio_unitario=Decimal('15.00'),
            cantidad=2,
            subtotal=Decimal('30.00'),
        )

        pedido_reciente = self._crear_pedido(estado='pendiente', pagado=False, metodo='bank_transfer', horas=1)
        DetallePedido.objects.create(
            pedido=pedido_reciente,
            producto=producto,
            variante=variante,
            nombre_producto=producto.nombre,
            precio_unitario=Decimal('15.00'),
            cantidad=1,
            subtotal=Decimal('15.00'),
        )

        pedido_pagado = self._crear_pedido(estado='pendiente', pagado=True, metodo='bank_transfer', horas=4)
        DetallePedido.objects.create(
            pedido=pedido_pagado,
            producto=producto,
            variante=variante,
            nombre_producto=producto.nombre,
            precio_unitario=Decimal('15.00'),
            cantidad=1,
            subtotal=Decimal('15.00'),
        )

        call_command('cancel_unpaid_orders', hours=2)

        pedido_objetivo.refresh_from_db()
        pedido_reciente.refresh_from_db()
        pedido_pagado.refresh_from_db()
        variante.refresh_from_db()

        self.assertEqual(pedido_objetivo.estado, 'cancelado')
        self.assertEqual(pedido_reciente.estado, 'pendiente')
        self.assertEqual(pedido_pagado.estado, 'pendiente')

        # Solo restaura las 2 unidades del pedido vencido.
        self.assertEqual(variante.stock, 5)

    def test_cancel_unpaid_orders_dry_run_no_modifica_datos(self):
        producto, variante = self._crear_producto_variante(stock=2)
        pedido_objetivo = self._crear_pedido(estado='pendiente', pagado=False, metodo='bank_transfer', horas=3)

        DetallePedido.objects.create(
            pedido=pedido_objetivo,
            producto=producto,
            variante=variante,
            nombre_producto=producto.nombre,
            precio_unitario=Decimal('15.00'),
            cantidad=2,
            subtotal=Decimal('30.00'),
        )

        call_command('cancel_unpaid_orders', hours=2, dry_run=True)

        pedido_objetivo.refresh_from_db()
        variante.refresh_from_db()

        self.assertEqual(pedido_objetivo.estado, 'pendiente')
        self.assertEqual(variante.stock, 2)
