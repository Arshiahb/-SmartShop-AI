from decimal import Decimal

import pytest

from apps.agent.services import ShoppingAgent
from apps.agent.tools import (
    compare_products,
    get_product_info,
    get_recommendations_for_product,
    search_catalog,
)
from apps.products.factories import ProductFactory


@pytest.mark.django_db
def test_catalog_tools_are_database_backed():
    product = ProductFactory(
        name="Pro Laptop",
        slug="pro-laptop-agent",
        price=Decimal("1200.00"),
        stock=4,
    )
    assert search_catalog("Pro Laptop")[0]["slug"] == product.slug
    assert get_product_info(product.slug)["price"] == "1200.00"
    assert compare_products([product.slug])[0]["name"] == "Pro Laptop"
    assert get_recommendations_for_product(product.slug) == []


def test_agent_message_structure_and_tool_execution(monkeypatch):
    monkeypatch.delenv("AGENT_API_KEY", raising=False)
    agent = ShoppingAgent()
    assert agent.messages()[0]["role"] == "system"
    assert agent.messages()[0]["content"] == agent.system_prompt
    assert agent.tool_result_json({"ok": True}) == '{"ok": true}'
