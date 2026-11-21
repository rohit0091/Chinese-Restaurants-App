from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import datetime
import random
import string
from .models import Order, OrderAddress, OrderItem, Payment, OrderStatusHistory
from cart.models import Cart, CartItem
from accounts.models import Address

def generate_order_number():
    """
    Generates a unique order string (e.g. MC-20260830-AB123).
    """
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"MC-{date_str}-{random_str}"

@login_required
def checkout_view(request):
    """
    Checkout controller. Handles address selection, payment routing, Order instantiation,
    OrderItem snapshots, payment state updates, and atomic cart clearing.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('food').all()
    
    if not cart_items.exists():
        messages.warning(request, "Your shopping cart is empty.")
        return redirect('menu')
        
    addresses = Address.objects.filter(user=request.user)
    
    # Calculate cart pricing
    subtotal = sum(item.food.final_price * item.quantity for item in cart_items)
    tax = round(subtotal * 0.05, 2)  # 5% tax
    delivery_fee = 40 if (subtotal < 300 and subtotal > 0) else 0
    total = subtotal + tax + delivery_fee
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'COD')
        special_instructions = request.POST.get('special_instructions', '').strip()
        
        selected_address = None
        if address_id:
            try:
                selected_address = Address.objects.get(id=address_id, user=request.user)
            except Address.DoesNotExist:
                pass
                
        if not selected_address:
            # Try to build a new address directly from post inputs
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address_line_1 = request.POST.get('address_line_1', '').strip()
            address_line_2 = request.POST.get('address_line_2', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            address_type = request.POST.get('address_type', 'HOME').strip()
            
            if not full_name or not phone or not address_line_1 or not city or not state or not pincode:
                messages.error(request, "Please select an existing address or fill out the new address form.")
                return redirect('checkout')
            else:
                selected_address = Address.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    landmark=landmark,
                    city=city,
                    state=state,
                    pincode=pincode,
                    address_type=address_type,
                    is_default=not Address.objects.filter(user=request.user).exists()
                )
                
        try:
            # Transaction block guarantees ACID reliability
            with transaction.atomic():
                order_num = generate_order_number()
                
                # 1. Create main order record
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_num,
                    subtotal=subtotal,
                    delivery_fee=delivery_fee,
                    tax=tax,
                    total_amount=total,
                    special_instructions=special_instructions,
                    status='PLACED'
                )
                
                # 2. Copy selected shipping address details
                OrderAddress.objects.create(
                    order=order,
                    full_name=selected_address.full_name,
                    phone=selected_address.phone,
                    address_line_1=selected_address.address_line_1,
                    address_line_2=selected_address.address_line_2,
                    landmark=selected_address.landmark,
                    city=selected_address.city,
                    state=selected_address.state,
                    pincode=selected_address.pincode,
                    address_type=selected_address.address_type
                )
                
                # 3. Create items list snapshot
                for item in cart_items:
                    unit_price = item.food.price
                    disc_amount = item.food.price * item.food.discount_percentage / 100
                    item_subtotal = item.food.final_price * item.quantity
                    
                    OrderItem.objects.create(
                        order=order,
                        food=item.food,
                        food_name=item.food.name,
                        quantity=item.quantity,
                        unit_price=unit_price,
                        discount=disc_amount,
                        subtotal=item_subtotal
                    )
                    
                # 4. Process mock payment status
                pay_status = 'PENDING'
                txn_id = ""
                paid_time = None
                if payment_method == 'MOCK_ONLINE':
                    pay_status = 'SUCCESS'
                    txn_id = f"TXN-{order_num}"
                    paid_time = timezone.now()
                    
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    payment_status=pay_status,
                    transaction_id=txn_id,
                    amount=total,
                    paid_at=paid_time
                )
                
                # 5. Add initial audit history entry
                OrderStatusHistory.objects.create(
                    order=order,
                    status='PLACED',
                    note="Order placed by customer during checkout."
                )
                
                # 6. Atomic checkout cart clearance
                cart_items.delete()
                
            messages.success(request, f"Order {order_num} placed successfully!")
            return redirect('order_success', order_id=order.id)
            
        except Exception as err:
            messages.error(request, f"An error occurred while processing checkout: {str(err)}")
            return redirect('cart')
            
    context = {
        'items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'tax': tax,
        'delivery_fee': delivery_fee,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_success_view(request, order_id):
    """
    Renders billing confirmation receipt.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})

@login_required
def order_history_view(request):
    """
    Lists past orders.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail_view(request, order_number):
    """
    Renders detailed order summaries, items bought, address snapshots, and status tracking.
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    items = order.items.all()
    history = order.status_history.order_by('created_at')
    
    # Track steps visual config
    steps = ['PLACED', 'CONFIRMED', 'PREPARING', 'READY', 'OUT_FOR_DELIVERY', 'DELIVERED']
    current_status = order.status
    
    # Calculate status index
    current_idx = -1
    if current_status in steps:
        current_idx = steps.index(current_status)
    elif current_status == 'CANCELLED':
        current_idx = -2  # Special identifier
        
    context = {
        'order': order,
        'items': items,
        'history': history,
        'steps': steps,
        'current_idx': current_idx,
    }
    return render(request, 'orders/order_detail.html', context)
