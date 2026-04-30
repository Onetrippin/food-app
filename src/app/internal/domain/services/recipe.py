from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.interfaces.recipe import RecipeRepositoryInterface


class RecipeService:
    def __init__(self, repository: RecipeRepositoryInterface) -> None:
        self._repository = repository

    def list_recipes(self) -> list[RecipeEntity]:
        return self._repository.list()

    def get_recipe(self, recipe_id: int) -> RecipeEntity:
        recipe = self._repository.get_by_id(recipe_id)

        if recipe is None:
            raise ValueError("Recipe not found.")

        return recipe

    def search_recipes(self, query: str) -> list[RecipeEntity]:
        return self._repository.search(query=query)

    def find_recipes_by_ingredients(self, available_ingredients: list[str]) -> list[RecipeEntity]:
        normalized_available_ingredients = [
            ingredient.strip()
            for ingredient in available_ingredients
            if ingredient.strip()
        ]

        if not normalized_available_ingredients:
            raise ValueError("At least one ingredient is required.")

        return self._repository.find_by_ingredients(
            available_ingredients=normalized_available_ingredients
        )
