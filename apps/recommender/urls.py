from django.urls import path

from . import views

app_name = "recommender"

urlpatterns = [
    path("for-you/", views.user_recommendations, name="for_user"),
    path("similar/<slug:slug>/", views.similar_products, name="similar"),
]
