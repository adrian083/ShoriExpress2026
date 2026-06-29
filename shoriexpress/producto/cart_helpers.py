from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from .cart import Cart


def wants_json(request):
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.GET.get('ajax') == '1'
        or request.POST.get('ajax') == '1'
    )


def cart_payload(cart):
    items = []
    total = 0.0
    count = 0
    for pid, value in cart.cart.items():
        qty = int(value.get('cantidad', 0))
        precio = float(value.get('precio', 0))
        line_total = precio * qty
        total += line_total
        count += qty
        items.append({
            'producto_id': int(value.get('producto_id') or pid),
            'nombre': value.get('nombre', ''),
            'precio': value.get('precio', '0'),
            'cantidad': qty,
            'total': f'{line_total:.2f}',
        })
    return {
        'cart_count': count,
        'cart_items_count': len(items),
        'cart_total': round(total, 2),
        'cart_total_display': f'{total:.2f}',
        'items': items,
    }


def cart_action_response(request, *, message, message_type='info', redirect_name='ver_carrito'):
    cart = Cart(request)
    if wants_json(request):
        return JsonResponse({
            'success': message_type != 'error',
            'message': message,
            'type': message_type,
            **cart_payload(cart),
        })
    tag = message_type if message_type in ('success', 'error', 'warning', 'info') else 'info'
    getattr(messages, tag)(request, message)
    return redirect(redirect_name)
