from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    products = Product.objects.select_related("category", "brand").prefetch_related("images")

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__name__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)

    from apps.recommender.services import recommend_for_user

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "query": query,
        "selected_category": category_slug,
        "user_recommendations": (
            recommend_for_user(request.user) if request.user.is_authenticated else []
        ),
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, "products/partials/product_results.html", context)
    return render(request, "products/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related("images"),
        slug=slug,
    )
    from apps.recommender.services import recommend_similar_products

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "similar_products": recommend_similar_products(product),
        },
    )
