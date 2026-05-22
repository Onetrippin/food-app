from __future__ import annotations

from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipeEntity:
    title: str
    description: str = ""
    ingredients: list[str] | None = None
    author_id: int | None = None
    author_username: str | None = None
    price_amount: Decimal = Decimal("0.00")
    price_currency: str = "RUB"
    is_published: bool = True
    views_count: int = 0
    likes_count: int = 0
    favorites_count: int = 0
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
