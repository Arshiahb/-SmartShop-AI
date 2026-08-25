from django.db import transaction

from apps.cart.services import Cart
from apps.products.models import Product

from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(user, cart: Cart, address):
    cart_items = list(cart.cart.items())
    if not cart_items:
        raise ValueError("Cannot create an order from an empty cart.")

    product_ids = [int(product_id) for product_id, _ in cart_items]
    products = Product.objects.select_for_update().filter(pk__in=product_ids)
    products_by_id = {product.pk: product for product in products}
    if len(products_by_id) != len(product_ids):
        raise ValueError("One or more products are no longer available.")

    order = Order.objects.create(user=user, address=address)
    total_amount = 0
    for product_id, quantity in cart_items:
        quantity = int(quantity)
        product = products_by_id[int(product_id)]
        if quantity < 1 or product.stock < quantity:
            raise ValueError(f"Insufficient stock for product {product.pk}.")
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )
        product.stock -= quantity
        product.save(update_fields=["stock", "updated_at"])
        total_amount += product.price * quantity

    order.total_amount = total_amount
    order.save(update_fields=["total_amount", "updated_at"])
    cart.clear()
    return order
