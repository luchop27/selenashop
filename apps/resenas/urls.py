from django.urls import path
from . import views

app_name = 'resenas'

urlpatterns = [
    path('submit/<int:producto_id>/', views.submit_review, name='submit_review'),
    path('reply/<int:resena_id>/', views.reply_review, name='reply_review'),
    path('get/<int:producto_id>/', views.get_reviews, name='get_reviews'),
]
