from django.shortcuts import render
from menu.models import Category, Food, Offer

def home_view(request):
    """
    Homepage view rendering special items, categories, and offers.
    """
    categories = Category.objects.filter(is_active=True)[:6]
    featured_foods = Food.objects.filter(is_available=True, is_featured=True)[:6]
    special_foods = Food.objects.filter(is_available=True, is_special=True)[:6]
    active_offers = Offer.objects.filter(is_active=True)[:3]
    
    context = {
        'categories': categories,
        'featured_foods': featured_foods,
        'special_foods': special_foods,
        'active_offers': active_offers,
    }
    return render(request, 'home/index.html', context)
