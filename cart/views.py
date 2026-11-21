from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from menu.models import Food

@login_required
def cart_view(request):
    """
    Renders cart items, computes subtotal, tax (5%), and conditional delivery fee.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('food').all()
    
    # Calculate cart total
    subtotal = sum(item.food.final_price * item.quantity for item in items)
    tax = round(subtotal * 0.05, 2)  # 5% GST tax example
    delivery_fee = 40 if (subtotal < 300 and subtotal > 0) else 0  # Free delivery above Rs. 300
    total = subtotal + tax + delivery_fee
    
    context = {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'delivery_fee': delivery_fee,
        'total': total,
    }
    return render(request, 'cart/cart.html', context)

@login_required
def add_to_cart(request, food_id):
    """
    Adds a food item to the shopping cart, or increments quantity if already present.
    """
    food = get_object_or_404(Food, id=food_id, is_available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, food=food)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Increased quantity of {food.name} in cart.")
    else:
        messages.success(request, f"Added {food.name} to cart.")
        
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

@login_required
def update_cart(request, item_id):
    """
    Increases or decreases cart item quantity. Evicts item if quantity drops below 1.
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action') or request.GET.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.success(request, f"Removed {cart_item.food.name} from cart.")
            return redirect('cart')
            
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """
    Removes an item completely from the shopping cart.
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    food_name = cart_item.food.name
    cart_item.delete()
    messages.success(request, f"Removed {food_name} from cart.")
    return redirect('cart')
