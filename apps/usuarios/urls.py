from django.urls import path
from . import views
from .views_password_reset import (
    password_reset_request_code,
    password_reset_verify,
    password_reset_complete,
    password_reset_resend
)

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_usuario, name='login'),
    path('register/', views.registrar_usuario, name='register'),
    path('logout/', views.logout_usuario, name='logout'),
    
    # API para ciudades por provincia (AJAX)
    path('api/ciudades-por-provincia/<int:provincia_id>/', views.api_ciudades_por_provincia, name='api_ciudades_por_provincia'),
    
    # Recuperación de contraseña con CÓDIGO DE 6 DÍGITOS
    path('password-reset/', password_reset_request_code, name='password_reset_request'),
    path('password-reset/verify/', password_reset_verify, name='password_reset_verify'),
    path('password-reset/complete/', password_reset_complete, name='password_reset_complete'),
    path('password-reset/resend/', password_reset_resend, name='password_reset_resend'),
    
    # Verificación de email
    path('verificar-email/<uuid:token>/', views.verificar_email, name='verificar_email'),
    path('reenviar-verificacion/', views.reenviar_verificacion, name='reenviar_verificacion'),
    
    # Panel de usuario
    path('my-account/', views.my_account, name='my_account'),
    path('my-account/orders/', views.my_account_orders, name='my_account_orders'),
    path('my-account/orders/<str:numero_pedido>/', views.my_account_orders_details, name='my_account_orders_details'),
    path('my-account/address/', views.my_account_address, name='my_account_address'),
    path('my-account/edit/', views.my_account_edit, name='my_account_edit'),
    path('my-account/wishlist/', views.my_account_wishlist, name='my_account_wishlist'),
    
    # Wishlist AJAX
    path('wishlist/add/<int:producto_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/check/<int:producto_id>/', views.is_in_wishlist, name='is_in_wishlist'),
]
