# producto/context_processor.py
from .cart import Cart

def cart_total_amount(request):
    cart = Cart(request)
    total = 0
    for key, value in cart.cart.items():
        total += float(value["precio"]) * value["cantidad"]
    return {'cart_total_amount': total, 'cart_count': len(cart.cart)}