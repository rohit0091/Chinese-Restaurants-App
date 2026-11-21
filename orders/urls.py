from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('history/', views.order_history_view, name='order_history'),
    path('track/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
