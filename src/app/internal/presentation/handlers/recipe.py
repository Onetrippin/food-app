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


def create_recipe_handler(
    author_id: int,
    title: str,
    description: str,
    ingredients: list[str],
) -> dict[str, object]:
    service = RecipeService(repository=DjangoRecipeRepository())

    try:
        recipe = service.create_recipe(
            author_id=author_id,
            title=title,
            description=description,
            ingredients=ingredients,
        )
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return _serialize_recipe(recipe)


def update_recipe_handler(
    actor_id: int,
    actor_is_staff: bool,
    recipe_id: int,
    title: str,
    description: str,
    ingredients: list[str],
) -> dict[str, object]:
    service = RecipeService(repository=DjangoRecipeRepository())

    try:
        recipe = service.update_recipe(
            actor_id=actor_id,
            actor_is_staff=actor_is_staff,
            recipe_id=recipe_id,
            title=title,
            description=description,
            ingredients=ingredients,
        )
    except PermissionError as error:
        raise HttpError(403, str(error)) from error
    except ValueError as error:
        status_code = 404 if str(error) == "Recipe not found." else 400
        raise HttpError(status_code, str(error)) from error

    return _serialize_recipe(recipe)


def add_recipe_to_favorites_handler(user_id: int, recipe_id: int) -> dict[str, str]:
    service = RecipeService(repository=DjangoRecipeRepository())

    try:
        service.add_recipe_to_favorites(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Recipe added to favorites."}


def remove_recipe_from_favorites_handler(user_id: int, recipe_id: int) -> dict[str, str]:
    service = RecipeService(repository=DjangoRecipeRepository())

    try:
        service.remove_recipe_from_favorites(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Recipe removed from favorites."}


def list_favorite_recipes_handler(user_id: int) -> list[dict[str, object]]:
    service = RecipeService(repository=DjangoRecipeRepository())
    return [_serialize_recipe(recipe) for recipe in service.list_favorite_recipes(user_id=user_id)]


def _serialize_recipe(recipe: RecipeEntity) -> dict[str, object]:
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients or [],
        "author_id": recipe.author_id,
        "author_username": recipe.author_username,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
    }
