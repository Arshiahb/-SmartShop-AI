from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.cart.services import Cart
from apps.orders.models import Order
from apps.orders.services import create_order_from_cart
from apps.products.factories import ProductFactory


@pytest.mark.django_db
def test_create_order_records_snapshot_and_decrements_stock():
    user = get_user_model().objects.create_user(username="buyer", password="test-pass")
    product = ProductFactory(price=Decimal("99.90"), stock=5)
    session = {}
    cart = Cart(session)
    cart.add(product, 2)

    order = create_order_from_cart(user, cart, "123 Main Street")

    product.refresh_from_db()
    item = order.items.get()
    assert order.status == Order.Status.PENDING
    assert product.stock_quantity == 3
    assert item.price == Decimal("99.90")
    assert item.quantity == 2
    assert order.total_amount == Decimal("199.80")
    assert len(cart) == 0


@pytest.mark.django_db
def test_order_fails_without_stock_and_does_not_create_order():
    user = get_user_model().objects.create_user(username="buyer-2", password="test-pass")
    product = ProductFactory(stock=1)
    session = {}
    cart = Cart(session)
    cart.add(product, 2)

    with pytest.raises(ValueError, match="Insufficient stock"):
        create_order_from_cart(user, cart, "123 Main Street")

    assert not Order.objects.filter(user=user).exists()
