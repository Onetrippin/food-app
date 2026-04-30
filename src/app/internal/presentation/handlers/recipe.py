from ninja.errors import HttpError

from app.internal.data.repositories.recipe import DjangoRecipeRepository
from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.services.recipe import RecipeService


def list_recipes_handler() -> list[dict[str, object]]:
    service = RecipeService(repository=DjangoRecipeRepository())
    return [_serialize_recipe(recipe) for recipe in service.list_recipes()]


def get_recipe_handler(recipe_id: int) -> dict[str, object]:
    service = RecipeService(repository=DjangoRecipeRepository())

    try:
        recipe = service.get_recipe(recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return _serialize_recipe(recipe)


def search_recipes_handler(query: str) -> list[dict[str, object]]:
    service = RecipeService(repository=DjangoRecipeRepository())
    return [_serialize_recipe(recipe) for recipe in service.search_recipes(query=query)]


def find_recipes_by_ingredients_handler(available_ingredients: list[str]) -> list[dict[str, object]]:
    service = RecipeService(repository=DjangoRecipeRepository())

    try:
        recipes = service.find_recipes_by_ingredients(
            available_ingredients=available_ingredients
        )
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return [_serialize_recipe(recipe) for recipe in recipes]


def _serialize_recipe(recipe: RecipeEntity) -> dict[str, object]:
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients or [],
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
    }
