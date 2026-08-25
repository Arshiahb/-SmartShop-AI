from decimal import Decimal

from django.db.models import Sum

from apps.orders.models import Order, OrderItem
from apps.products.models import Product


def extract_features(product):
    """Return a deterministic, human-readable feature representation."""
    specifications = product.specifications or {}
    return {
        "category": product.category_id,
        "brand": product.brand_id,
        "price": Decimal(product.price),
        "rating": Decimal(product.average_rating),
        "specifications": {
            str(key).lower(): str(value).lower() for key, value in specifications.items()
        },
    }


def _specification_similarity(left, right):
    left_specs = left["specifications"]
    right_specs = right["specifications"]
    if not left_specs and not right_specs:
        return 1.0
    keys = set(left_specs) | set(right_specs)
    return sum(left_specs.get(key) == right_specs.get(key) for key in keys) / len(keys)


def _content_score(source, candidate):
    source_features = extract_features(source)
    candidate_features = extract_features(candidate)
    score = 0.0
    score += 0.35 if source_features["category"] == candidate_features["category"] else 0
    score += 0.25 if source_features["brand"] == candidate_features["brand"] else 0

    max_price = max(source_features["price"], candidate_features["price"], Decimal("1"))
    price_similarity = 1 - min(
        abs(source_features["price"] - candidate_features["price"]) / max_price,
        Decimal("1"),
    )
    score += 0.20 * float(price_similarity)

    rating_similarity = 1 - min(
        abs(source_features["rating"] - candidate_features["rating"]) / Decimal("5"),
        Decimal("1"),
    )
    score += 0.10 * float(rating_similarity)
    score += 0.10 * _specification_similarity(source_features, candidate_features)
    return round(score, 6)


def recommend_similar_products(product, limit=5):
    candidates = (
        Product.objects.select_related("category", "brand")
        .exclude(pk=product.pk)
        .filter(stock__gt=0)
    )
    ranked = sorted(
        ((candidate, _content_score(product, candidate)) for candidate in candidates),
        key=lambda item: (-item[1], item[0].pk),
    )
    return [candidate for candidate, _score in ranked[:limit]]


def recommend_for_user(user, limit=5):
    if not getattr(user, "is_authenticated", False):
        return Product.objects.none()

    purchased = (
        OrderItem.objects.filter(
            order__user=user,
            order__status__in=[Order.Status.CONFIRMED, Order.Status.PENDING],
        )
        .values("product_id")
        .annotate(weight=Sum("quantity"))
    )
    purchased_ids = {row["product_id"] for row in purchased}
    if not purchased_ids:
        return Product.objects.filter(stock__gt=0).order_by(
            "-average_rating",
            "-created_at",
        )[:limit]

    source_products = list(
        Product.objects.select_related("category", "brand").filter(pk__in=purchased_ids)
    )
    candidates = (
        Product.objects.select_related("category", "brand")
        .exclude(pk__in=purchased_ids)
        .filter(stock__gt=0)
    )
    ranked = []
    for candidate in candidates:
        scores = [_content_score(source, candidate) for source in source_products]
        ranked.append((candidate, max(scores)))
    ranked.sort(key=lambda item: (-item[1], item[0].pk))
    return [candidate for candidate, _score in ranked[:limit]]
