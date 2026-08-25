import factory
from factory.django import DjangoModelFactory

from .models import Brand, Category, Product, ProductImage


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class BrandFactory(DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f"Brand {n}")
    slug = factory.Sequence(lambda n: f"brand-{n}")
    description = factory.Faker("sentence")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Digital Product {n}")
    slug = factory.Sequence(lambda n: f"digital-product-{n}")
    description = factory.Faker("paragraph")
    price = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    stock = factory.Faker("pyint", min_value=0, max_value=500)
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    specifications = factory.LazyFunction(
        lambda: {"storage": "256GB", "warranty_months": 12, "connectivity": "Wi-Fi"}
    )
    average_rating = factory.Faker(
        "pydecimal",
        left_digits=1,
        right_digits=2,
        positive=True,
        max_value=5,
    )


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image_url = factory.Faker("image_url")


def create_500_products():
    """Create and return 500 synthetic products for development/test data."""
    return ProductFactory.create_batch(500)
