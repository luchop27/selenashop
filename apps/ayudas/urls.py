from django.urls import path
from . import views

app_name = 'ayudas'

urlpatterns = [
    path('terminos-condiciones/', views.terms_conditions, name='terms-conditions'),
    path('devoluciones-cambios/', views.delivery_return, name='delivery-return'),
    path('envios/', views.shipping, name='shipping'),
    path('politica-privacidad/', views.privacy_policy, name='privacy-policy'),
    path('faq/', views.faq_list, name='faq'),
]

