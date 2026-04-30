from __future__ import annotations

from typing import Protocol

from app.internal.domain.entities.recipe import RecipeEntity


class RecipeRepositoryInterface(Protocol):
    def list(self) -> list[RecipeEntity]:
        ...

    def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        ...

    def search(self, query: str) -> list[RecipeEntity]:
        ...

    def find_by_ingredients(self, available_ingredients: list[str]) -> list[RecipeEntity]:
        ...
