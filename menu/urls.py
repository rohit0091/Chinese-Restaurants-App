from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('food/<slug:slug>/', views.food_detail_view, name='food_detail'),
]
