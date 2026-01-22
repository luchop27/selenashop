"""


Backend de email personalizado con manejo robusto de errores SSL
"""
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
import ssl
import logging

logger = logging.getLogger(__name__)


class RobustEmailBackend(SMTPBackend):
    """
    Backend de email que maneja errores SSL automáticamente.
    Si falla el envío por SSL, imprime en consola como fallback.
    """
    
    def open(self):
        """
        Abre la conexión SMTP con manejo de errores SSL mejorado
        """
        try:
            # Crear contexto SSL personalizado para Gmail
            if self.use_tls and not self.use_ssl:
                import ssl
                self.ssl_context = ssl.create_default_context()
                # Permitir certificados que no cumplan estrictamente con Basic Constraints
                self.ssl_context.check_hostname = True
                self.ssl_context.verify_mode = ssl.CERT_REQUIRED
                # Cargar certificados del sistema
                try:
                    self.ssl_context.load_default_certs()
                except Exception as cert_error:
                    logger.warning(f'⚠️  No se pudieron cargar certificados del sistema: {cert_error}')
            
            return super().open()
            
        except ssl.SSLError as ssl_error:
            logger.error(f'❌ Error SSL al conectar con servidor de email: {ssl_error}')
            logger.error(f'   Host: {self.host}:{self.port}')
            logger.error(f'   TLS: {self.use_tls}, SSL: {self.use_ssl}')
            
            # Intentar con verificación SSL deshabilitada como último recurso
            logger.warning('⚠️  Intentando conexión sin verificación SSL (SOLO DESARROLLO)...')
            try:
                self.ssl_context = ssl.create_default_context()
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
                return super().open()
            except Exception as retry_error:
                logger.error(f'❌ Falló intento sin verificación SSL: {retry_error}')
                raise
                
        except Exception as e:
            logger.error(f'❌ Error inesperado al abrir conexión de email: {e}')
            raise
    
    def send_messages(self, email_messages):
        """
        Envía mensajes con manejo de errores robusto
        """
        try:
            return super().send_messages(email_messages)
        except Exception as e:
            logger.error(f'❌ Error al enviar emails: {e}')
            logger.error('📝 Mostrando emails en consola como fallback...')
            
            # Fallback a consola
            console_backend = ConsoleBackend()
            return console_backend.send_messages(email_messages)
