from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

from . import tools

SYSTEM_PROMPT = (
    "You are SmartShop AI's shopping assistant. Use only catalog-backed tools for "
    "product facts, prices, stock, comparisons, and recommendations. Never invent "
    "products or attributes. If an exact match is unavailable, use catalog-backed "
    "similar or popular products and explain that they are alternatives."
)
MAX_MESSAGE_LENGTH = 2000


class ShoppingAgent:
    """Manage conversation history and optional OpenAI-compatible tool calling."""

    tool_registry: dict[str, Callable[..., Any]] = {
        "search_catalog": tools.search_catalog,
        "get_product_info": tools.get_product_info,
        "compare_products": tools.compare_products,
        "get_recommendations_for_product": tools.get_recommendations_for_product,
    }

    def __init__(self, history: list[dict[str, Any]] | None = None):
        self.history = history or []
        self.system_prompt = SYSTEM_PROMPT
        self.api_key = os.getenv("AGENT_API_KEY", "")
        self.base_url = os.getenv("AGENT_BASE_URL", "")
        self.model = os.getenv("AGENT_MODEL", "gpt-4o-mini")

    def messages(self) -> list[dict[str, str]]:
        """Return normalized system and conversation messages."""
        return [{"role": "system", "content": self.system_prompt}, *self.history]

    def _mock_response(self, user_message: str) -> str:
        """Produce a deterministic catalog-backed response when no API key is configured."""
        results = tools.search_catalog(user_message, limit=3)
        lines = ["بر اساس کاتالوگ فعلی، این محصولات مرتبط یا جایگزین پیشنهاد می‌شوند:"]
        lines.extend(
            f"- {item['name']} | قیمت: {item['price']} | موجودی: {item['stock']}"
            for item in results
        )
        return "\n".join(lines)

    def _client(self):
        from openai import OpenAI

        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return OpenAI(**kwargs)

    def _tool_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_catalog",
                    "description": "Search the live product catalog.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "max_price": {"type": ["number", "null"]},
                            "category": {"type": ["string", "null"]},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Get authoritative facts for a product slug.",
                    "parameters": {
                        "type": "object",
                        "properties": {"slug": {"type": "string"}},
                        "required": ["slug"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_products",
                    "description": "Compare products by their slugs.",
                    "parameters": {
                        "type": "object",
                        "properties": {"slugs": {"type": "array", "items": {"type": "string"}}},
                        "required": ["slugs"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommendations_for_product",
                    "description": "Find similar products from the live catalog.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slug": {"type": "string"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                        },
                        "required": ["slug"],
                    },
                },
            },
        ]

    def reply(self, user_message: str) -> str:
        """Append a user message and return an API or safe catalog-backed mock response."""
        if not isinstance(user_message, str) or not user_message.strip():
            raise ValueError("Message cannot be empty.")
        if len(user_message) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message cannot exceed {MAX_MESSAGE_LENGTH} characters.")
        user_message = user_message.strip()
        self.history.append({"role": "user", "content": user_message})
        if not self.api_key:
            answer = self._mock_response(user_message)
            self.history.append({"role": "assistant", "content": answer})
            return answer

        client = self._client()
        messages = self.messages()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._tool_schemas(),
            tool_choice="auto",
            temperature=0.2,
            timeout=30,
        )
        for _ in range(3):
            message = response.choices[0].message
            if not message.tool_calls:
                break
            messages.append(message.model_dump(exclude_none=True))
            for tool_call in message.tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    result = self.run_tool(tool_call.function.name, arguments)
                except (TypeError, ValueError, json.JSONDecodeError):
                    result = {"error": "Invalid catalog tool request."}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": self.tool_result_json(result),
                    }
                )
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._tool_schemas(),
                tool_choice="auto",
                temperature=0.2,
                timeout=30,
            )
        answer = response.choices[0].message.content or "پاسخی از ایجنت دریافت نشد."
        self.history.append({"role": "assistant", "content": answer})
        return answer

    def run_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a registered catalog tool by name with validated arguments."""
        if name not in self.tool_registry:
            raise ValueError(f"Unknown tool: {name}")
        return self.tool_registry[name](**arguments)

    @staticmethod
    def tool_result_json(result: Any) -> str:
        """Serialize tool output for an OpenAI-compatible tool result message."""
        return json.dumps(result, ensure_ascii=False, default=str)
