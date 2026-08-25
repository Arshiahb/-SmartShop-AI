from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Q

from apps.products.models import Product
from apps.recommender.services import recommend_similar_products


def _serialize_product(product: Product) -> dict[str, Any]:
    return {
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock_quantity,
        "category": product.category.name,
        "brand": product.brand.name,
        "rating": str(product.average_rating),
        "specifications": product.specifications or {},
    }


def search_catalog(
    query: str,
    max_price: Decimal | float | int | None = None,
    category: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Search available catalog products by text, price ceiling, and category slug/name."""
    base = Product.objects.select_related("category", "brand").filter(stock__gt=0)
    products = base
    if query:
        terms = [term for term in query.split() if term]
        text_query = Q()
        for term in terms:
            text_query |= (
                Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(brand__name__icontains=term)
                | Q(category__name__icontains=term)
            )
        products = base.filter(text_query)
    if max_price is not None:
        products = products.filter(price__lte=Decimal(str(max_price)))
    if category:
        products = products.filter(
            Q(category__slug__iexact=category) | Q(category__name__icontains=category)
        )
    results = list(products.distinct()[: max(1, limit)])
    if results:
        return [_serialize_product(product) for product in results]

    fallback = base
    if category:
        fallback = fallback.filter(
            Q(category__slug__iexact=category) | Q(category__name__icontains=category)
        )
    if query:
        fallback_terms = [term for term in query.split() if len(term) >= 3]
        if fallback_terms:
            fuzzy_query = Q()
            for term in fallback_terms:
                fuzzy_query |= (
                    Q(name__icontains=term)
                    | Q(description__icontains=term)
                    | Q(brand__name__icontains=term)
                    | Q(category__name__icontains=term)
                )
            fuzzy_results = list(fallback.filter(fuzzy_query).distinct()[: max(1, limit)])
            if fuzzy_results:
                return [_serialize_product(product) for product in fuzzy_results]
    return [
        _serialize_product(product)
        for product in fallback.order_by("-average_rating", "-created_at")[: max(1, limit)]
    ]


def get_product_info(slug: str) -> dict[str, Any] | None:
    """Return authoritative product details, price, stock, and specifications by slug."""
    product = Product.objects.select_related("category", "brand").filter(slug=slug).first()
    return _serialize_product(product) if product else None


def compare_products(slugs: list[str]) -> list[dict[str, Any]]:
    """Return a database-backed comparison for the requested product slugs."""
    products = Product.objects.select_related("category", "brand").filter(slug__in=slugs)
    by_slug = {product.slug: _serialize_product(product) for product in products}
    return [by_slug[slug] for slug in slugs if slug in by_slug]


def get_recommendations_for_product(slug: str, limit: int = 3) -> list[dict[str, Any]]:
    """Return database-backed similar products using the recommender service."""
    product = Product.objects.select_related("category", "brand").filter(slug=slug).first()
    if not product:
        return []
    return [_serialize_product(item) for item in recommend_similar_products(product, limit)]
