from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.orders.models import Order, OrderItem
from apps.products.factories import BrandFactory, CategoryFactory, ProductFactory
from apps.recommender.services import (
    extract_features,
    recommend_for_user,
    recommend_similar_products,
)


@pytest.mark.django_db
def test_similar_products_prioritizes_same_category_and_brand():
    category = CategoryFactory()
    brand = BrandFactory()
    source = ProductFactory(category=category, brand=brand, price=Decimal("100.00"))
    best = ProductFactory(
        category=category,
        brand=brand,
        price=Decimal("105.00"),
        specifications={"storage": "256GB"},
    )
    ProductFactory(price=Decimal("900.00"), stock=10)

    assert extract_features(source)["category"] == category.id
    assert recommend_similar_products(source, limit=1)[0] == best


@pytest.mark.django_db
def test_user_recommendations_exclude_purchased_products_and_use_purchase_history():
    user = get_user_model().objects.create_user(username="recommender-user")
    category = CategoryFactory()
    brand = BrandFactory()
    purchased = ProductFactory(category=category, brand=brand)
    recommended = ProductFactory(category=category, brand=brand, price=Decimal("110.00"))
    unrelated = ProductFactory(price=Decimal("999.00"), stock=10)
    order = Order.objects.create(user=user, address="Test", status=Order.Status.CONFIRMED)
    OrderItem.objects.create(order=order, product=purchased, quantity=1, price=purchased.price)

    result = list(recommend_for_user(user, limit=2))
    assert purchased not in result
    assert recommended in result
    assert unrelated not in result[:1]
