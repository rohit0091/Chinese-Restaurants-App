from .models import Cart

def cart_renderer(request):
    """
    Context processor adding the authenticated user's cart item count to all templates.
    """
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            total_items = sum(item.quantity for item in cart.items.all())
            return {'cart_count': total_items}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
        except Exception:
            return {'cart_count': 0}
    return {'cart_count': 0}
