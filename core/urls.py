from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.products.urls")),
    path("cart/", include("apps.cart.urls")),
    path("recommendations/", include("apps.recommender.urls")),
    path("agent/", include("apps.agent.urls")),
]
