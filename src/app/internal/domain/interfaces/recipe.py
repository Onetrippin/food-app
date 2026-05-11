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

    def create(
        self,
        author_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        is_published: bool,
    ) -> RecipeEntity:
        ...

    def update(
        self,
        recipe_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        is_published: bool,
    ) -> RecipeEntity | None:
        ...

    def add_to_favorites(self, user_id: int, recipe_id: int) -> None:
        ...

    def remove_from_favorites(self, user_id: int, recipe_id: int) -> None:
        ...

    def list_favorites(self, user_id: int) -> list[RecipeEntity]:
        ...

    def add_like(self, user_id: int, recipe_id: int) -> None:
        ...

    def remove_like(self, user_id: int, recipe_id: int) -> None:
        ...

    def increment_views(self, recipe_id: int) -> None:
        ...

    def delete(self, recipe_id: int) -> bool:
        ...

    def list_by_author(self, author_id: int) -> list[RecipeEntity]:
        ...
