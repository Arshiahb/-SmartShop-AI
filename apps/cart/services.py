from decimal import Decimal

from apps.products.models import Product


class Cart:
    session_key = "cart"

    def __init__(self, session):
        self.session = session
        self.cart = session.setdefault(self.session_key, {})

    def add(self, product, quantity=1):
        product_id = str(product.pk)
        current_quantity = int(self.cart.get(product_id, 0))
        self.cart[product_id] = current_quantity + int(quantity)
        self._save()

    def remove(self, product):
        self.cart.pop(str(product.pk), None)
        self._save()

    def get_total_price(self):
        products = Product.objects.filter(pk__in=self.cart.keys())
        prices = {str(product.pk): product.price for product in products}
        return sum(
            (
                prices[product_id] * quantity
                for product_id, quantity in self.cart.items()
                if product_id in prices
            ),
            Decimal("0.00"),
        )

    def clear(self):
        self.session[self.session_key] = {}
        self.cart = self.session[self.session_key]
        self._save()

    def items(self):
        products = Product.objects.filter(pk__in=self.cart.keys())
        return [(product, int(self.cart[str(product.pk)])) for product in products]

    def __len__(self):
        return sum(int(quantity) for quantity in self.cart.values())

    def _save(self):
        if hasattr(self.session, "modified"):
            self.session.modified = True
        else:
            self.session[self.session_key] = self.cart
