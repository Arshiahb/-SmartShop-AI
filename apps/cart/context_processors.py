from .services import Cart


def cart(request):
    current_cart = Cart(request.session)
    return {
        "cart_count": len(current_cart),
        "cart_total": current_cart.get_total_price(),
    }
