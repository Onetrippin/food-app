from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipeEntity:
    title: str
    description: str = ""
    ingredients: list[str] | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
