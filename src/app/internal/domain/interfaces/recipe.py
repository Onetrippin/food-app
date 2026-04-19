from __future__ import annotations

from typing import Protocol

from app.internal.domain.entities.recipe import RecipeEntity


class RecipeRepositoryInterface(Protocol):
    def list(self) -> list[RecipeEntity]:
        ...
