from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Food, Review
from orders.models import Order, OrderItem
from django.db.models import Avg

def menu_view(request):
    """
    Renders the menu page with categories, searching, and filtering.
    """
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    food_type = request.GET.get('type', '').strip()
    spice_level = request.GET.get('spice', '').strip()
    
    categories = Category.objects.filter(is_active=True)
    foods = Food.objects.filter(is_available=True)
    
    if query:
        foods = foods.filter(name__icontains=query) | foods.filter(description__icontains=query)
        
    if category_slug:
        foods = foods.filter(category__slug=category_slug)
        
    if food_type in ['VEG', 'NON_VEG']:
        foods = foods.filter(food_type=food_type)
        
    if spice_level in ['MILD', 'MEDIUM', 'HOT', 'EXTRA_HOT']:
        foods = foods.filter(spice_level=spice_level)
        
    context = {
        'categories': categories,
        'foods': foods,
        'query': query,
        'selected_category': category_slug,
        'selected_type': food_type,
        'selected_spice': spice_level,
    }
    return render(request, 'menu/menu.html', context)

def food_detail_view(request, slug):
    """
    Detailed food page. Displays item properties, average ratings, customer reviews,
    and handles review creation for users who purchased the item.
    """
    food = get_object_or_404(Food, slug=slug, is_available=True)
    reviews = food.reviews.filter(is_approved=True).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
    
    # Check if the current user can leave a review
    can_review = False
    purchased_order = None
    if request.user.is_authenticated:
        # Check if user has a delivered order containing this food, and hasn't reviewed it yet
        delivered_orders = Order.objects.filter(user=request.user, status='DELIVERED')
        for order in delivered_orders:
            # Check if this food was in the order
            has_food = OrderItem.objects.filter(order=order, food=food).exists()
            # Check if review already exists for this (user, food, order)
            reviewed = Review.objects.filter(user=request.user, food=food, order=order).exists()
            if has_food and not reviewed:
                can_review = True
                purchased_order = order
                break
                
    if request.method == 'POST' and can_review:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        try:
            rating_val = int(rating)
            if 1 <= rating_val <= 5:
                # Create review
                Review.objects.create(
                    user=request.user,
                    food=food,
                    order=purchased_order,
                    rating=rating_val,
                    comment=comment,
                    is_approved=True  # Auto-approve for simplified flow, or False if admin needs to approve
                )
                messages.success(request, "Thank you for your review!")
                return redirect('food_detail', slug=slug)
            else:
                messages.error(request, "Invalid rating value.")
        except (ValueError, TypeError):
            messages.error(request, "Please select a valid rating.")
            
    context = {
        'food': food,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'can_review': can_review,
    }
    return render(request, 'menu/food_detail.html', context)
