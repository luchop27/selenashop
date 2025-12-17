from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_usuario, name='login'),
    path('register/', views.registrar_usuario, name='register'),
    path('logout/', views.logout_usuario, name='logout'),
    
    # API para ciudades por provincia (AJAX)
    path('api/ciudades-por-provincia/<int:provincia_id>/', views.api_ciudades_por_provincia, name='api_ciudades_por_provincia'),
    
    # Recuperación de contraseña
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
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
]
