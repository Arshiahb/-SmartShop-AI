from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.products.models import Product

from .services import recommend_for_user, recommend_similar_products


def similar_products(request, slug):
    product = get_object_or_404(Product, slug=slug)
    products = recommend_similar_products(product)
    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            {
                "product": product.slug,
                "recommendations": [
                    {"id": item.id, "name": item.name, "slug": item.slug, "price": str(item.price)}
                    for item in products
                ],
            }
        )
    return render(
        request,
        "recommender/recommendation_list.html",
        {"title": "محصولات مشابه", "recommendations": products},
    )


@login_required
def user_recommendations(request):
    return render(
        request,
        "recommender/recommendation_list.html",
        {
            "title": "پیشنهادهای مخصوص شما",
            "recommendations": recommend_for_user(request.user),
        },
    )
