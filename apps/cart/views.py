from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from apps.products.models import Product

from .services import Cart


def _cart_context(request):
    current_cart = Cart(request.session)
    return {
        "cart": current_cart,
        "cart_items": current_cart.items(),
        "cart_count": len(current_cart),
        "cart_total": current_cart.get_total_price(),
    }


def cart_detail(request):
    return render(request, "cart/cart_detail.html", _cart_context(request))


def add_to_cart(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    product = get_object_or_404(Product, pk=product_id)
    quantity = max(int(request.POST.get("quantity", 1)), 1)
    current_cart = Cart(request.session)
    current_quantity = int(current_cart.cart.get(str(product.pk), 0))
    if current_quantity + quantity > product.stock:
        messages.warning(request, "تعداد درخواستی بیشتر از موجودی محصول است.")
    else:
        current_cart.add(product, quantity)
        messages.success(request, "محصول به سبد خرید اضافه شد.")
    return render(request, "cart/partials/cart_summary.html", _cart_context(request))


def update_cart(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get("quantity", 0))
    current_cart = Cart(request.session)
    if quantity <= 0:
        current_cart.remove(product)
    elif quantity <= product.stock:
        current_cart.cart[str(product.pk)] = quantity
        current_cart._save()
    else:
        messages.warning(request, "تعداد درخواستی بیشتر از موجودی محصول است.")
    return render(request, "cart/partials/cart_content.html", _cart_context(request))


def remove_from_cart(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    product = get_object_or_404(Product, pk=product_id)
    Cart(request.session).remove(product)
    return render(request, "cart/partials/cart_content.html", _cart_context(request))
