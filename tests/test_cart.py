from decimal import Decimal

import pytest

from apps.cart.services import Cart
from apps.products.factories import ProductFactory


@pytest.mark.django_db
def test_session_cart_add_total_remove_and_clear():
    product = ProductFactory(price=Decimal("25.00"))
    session = {}
    cart = Cart(session)

    cart.add(product, 2)
    assert len(cart) == 2
    assert cart.get_total_price() == Decimal("50.00")

    cart.remove(product)
    assert len(cart) == 0
    cart.add(product)
    cart.clear()
    assert len(cart) == 0
